"""AI generation orchestration for outlines, decks, and generated assets.

Architectural notes
-------------------
* Outline → approved outline → presentation build is synchronous (LLM only).
* Image generation is dispatched to background worker threads so the user
  receives a usable presentation immediately and the heavy SD calls run after.
* Job state lives in storage/image_jobs/<presentation_id>.json and is polled
  by the frontend; once a job finishes the frontend pulls the asset and
  patches the in-memory document.
"""

from __future__ import annotations

import base64
import json
import logging
import math
import os
import random
import re
import threading
import time
import uuid
from typing import Any
from urllib import error, parse, request

from pydantic import ValidationError

logger = logging.getLogger(__name__)

from .ai_models import (
    GenerationBasis,
    ImagePolicy,
    LayoutGenerationBasis,
    OutlineGenerationRequest,
    OutlineGenerationResponse,
    OutlineRetryRequest,
    OutlineSlide,
    PresentationBuildRequest,
    PresentationOutline,
    StyleGenerationBasis,
)
from .models import (
    Asset,
    BackgroundColor,
    LayoutDocument,
    PresentationDocument,
    PresentationTheme,
    SlideDocument,
    SlideSize,
    TemplateDocument,
    ThemeColors,
    ThemeFonts,
)
from .storage import (
    delete_image_jobs,
    get_generation,
    get_image_jobs,
    get_presentation,
    get_template,
    save_generation,
    save_image_jobs,
    save_presentation,
    store_asset,
)


class AiApiError(Exception):
    def __init__(self, status_code: int, detail: str | dict[str, Any]):
        self.status_code = status_code
        self.detail = detail
        super().__init__(str(detail))


ALLOWED_SLIDE_TYPES = {"title", "text", "image", "bullets", "conclusion"}
MOCK_IMAGE_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)

STYLE_THEMES: dict[str, PresentationTheme] = {
    "business": PresentationTheme(
        fonts=ThemeFonts(heading="Inter", body="Inter"),
        colors=ThemeColors(
            background="#0C1016",
            text="#F4F5F7",
            primary="#FFB547",
            secondary="#5A8FF0",
            accent="#38D2A4",
        ),
    ),
    "friendly": PresentationTheme(
        fonts=ThemeFonts(heading="Inter", body="Inter"),
        colors=ThemeColors(
            background="#F7F2EA",
            text="#20242C",
            primary="#2F80ED",
            secondary="#F2994A",
            accent="#27AE60",
        ),
    ),
    "academic": PresentationTheme(
        fonts=ThemeFonts(heading="Inter", body="Inter"),
        colors=ThemeColors(
            background="#F8FAFC",
            text="#102033",
            primary="#1D4ED8",
            secondary="#475569",
            accent="#0F766E",
        ),
    ),
    "promo": PresentationTheme(
        fonts=ThemeFonts(heading="Inter", body="Inter"),
        colors=ThemeColors(
            background="#101014",
            text="#FFFFFF",
            primary="#EF5D4A",
            secondary="#FFB547",
            accent="#5A8FF0",
        ),
    ),
}


STYLE_VISUAL_LANGUAGE: dict[str, str] = {
    "business": (
        "editorial photography or polished 3D render, dark navy / charcoal palette "
        "with warm amber and electric blue accents, premium B2B feel, soft cinematic lighting"
    ),
    "friendly": (
        "warm natural-light photography or hand-drawn flat illustration, "
        "cream/beige background, vivid orange and emerald accents, optimistic and approachable mood"
    ),
    "academic": (
        "clean minimalist photography or precise vector illustration, "
        "white/cool-grey palette with cobalt blue and teal accents, intellectual and rigorous tone"
    ),
    "promo": (
        "high-energy editorial photography or vibrant 3D scene, "
        "deep black background with neon coral, gold and electric blue, bold cinematic mood"
    ),
}


# ---------------------------------------------------------------------------
# LLM prompt construction
# ---------------------------------------------------------------------------

OUTLINE_SYSTEM_PROMPT = (
    "Ты — старший продюсер презентаций и сценарист, работающий с топ-менеджерами, "
    "стартапами и преподавателями. Ты пишешь конкретно, по делу и без штампов.\n\n"
    "ЖЁСТКИЕ ПРАВИЛА:\n"
    "1. Заголовки слайдов — это ТЕЗИСЫ, а не рубрики. Запрещены: «Введение», «Раздел 1..N», "
    "«Основная часть», «Тезис 1», «Контекст», «Главное», «Ключевой образ», «Выводы», "
    "«Заключение», «Спасибо за внимание», «Обзор», «О нас», «Цели», «Подход».\n"
    "2. Каждый заголовок — формулировка, у которой видна позиция автора. Пример «плохо»: "
    "«Финансовые показатели». Пример «хорошо»: «Выручка выросла на 38% за счёт enterprise — "
    "и это меняет приоритеты команды».\n"
    "3. Заголовок должен помещаться в 1–2 строки: обычно 45–75 символов. Длинную мысль переноси "
    "в keyPoints или speakerNotes.\n"
    "4. keyPoints — короткие, осмысленные тезисы (5–14 слов), желательно с цифрами, фактами "
    "или конкретными решениями. Никаких «Тезис 1 / Тезис 2».\n"
    "5. Каждый слайд должен раскрывать что-то новое. Не повторяй мысль из предыдущего слайда.\n"
    "6. Используй живой деловой русский язык, без канцелярита и общих мест.\n"
    "7. visualIntent — короткое описание визуала на русском (что должно быть на слайде, "
    "какая метафора). imagePrompt — детальный prompt для генерации изображения на АНГЛИЙСКОМ, "
    "конкретный, с указанием стиля, света, композиции и цветовой палитры. Запрещены слова "
    "text, words, letters, logo, watermark, caption — внутри картинки текста быть не должно.\n"
    "8. needsImage = true только если визуал реально усиливает мысль слайда. Не делай картинки "
    "ради картинок.\n\n"
    "Возвращай строго валидный JSON-объект без Markdown, без комментариев и без текста вокруг."
)

CONTENT_SYSTEM_PROMPT = (
    "Ты — редактор и сценарист презентаций. На вход получаешь утверждённое оглавление "
    "(заголовки и тезисы) и должен превратить его в готовое содержимое слайдов.\n\n"
    "ЖЁСТКИЕ ПРАВИЛА:\n"
    "1. Сохрани порядок и количество слайдов. Заголовки можно слегка отредактировать, "
    "если они шаблонны, но смысл не меняй.\n"
    "2. keyPoints — это финальный текст, который окажется на слайде. Каждая строка — "
    "цельная, законченная мысль (8–18 слов), без вводных «итак», «таким образом», «как мы видим». "
    "Используй конкретику: цифры, имена продуктов, действия, сроки.\n"
    "3. Запрещены штампы: «Тезис 1», «Раздел N», «Контекст», «Введение», «Заключение», "
    "«Главный вывод», «Ключевой образ», «Поддерживающий тезис», «Решение или действие», "
    "«Целевая аудитория из запроса», «Раскрыть часть темы».\n"
    "4. purpose — одна сильная фраза о роли слайда в нарративе (зачем он нужен в этой логике). "
    "Не пересказывай заголовок.\n"
    "5. speakerNotes — 2–3 предложения, что докладчик может сказать вслух, расширяя тезисы.\n"
    "6. visualIntent — на русском, что должно быть в кадре и почему. imagePrompt — на АНГЛИЙСКОМ, "
    "детальный prompt для генерации изображения: субъект, окружение, стиль, освещение, цветовая "
    "палитра под выбранный стиль презентации, композиция (rule of thirds, close-up, wide shot). "
    "Никакого текста на изображении, без логотипов, без водяных знаков.\n"
    "7. needsImage = true только если визуал реально работает на смысл слайда.\n\n"
    "Возвращай строго валидный JSON-объект без Markdown."
)

IMAGE_PROMPT_SYSTEM = (
    "You craft prompts for image generation. Output ONE concise English prompt "
    "(40-70 words) describing a single coherent scene. Include: subject, setting, "
    "art style, lighting, color palette, composition, mood. Add quality boosters "
    "like 'editorial photography', 'cinematic lighting', 'high detail'. "
    "Strict negatives: no text, no letters, no captions, no logos, no watermarks, "
    "no UI elements, no charts. Reply with just the prompt as plain text, no JSON, "
    "no quotes, no markdown."
)


def _outline_user_text(payload: dict[str, Any]) -> str:
    style_hint = _style_hint(payload.get("basis"))
    return (
        "Сгенерируй оглавление презентации по входному JSON.\n"
        f"Стиль и визуальный язык: {style_hint}.\n"
        "Ответ — валидный JSON-объект без Markdown.\n\n"
        "Формат ответа:\n"
        "{\n"
        '  "title": "string — заголовок презентации, цепляющий, без штампов",\n'
        '  "audience": "string — кому это адресовано, конкретно (роль/сегмент)",\n'
        '  "goal": "string — какое решение/действие должно состояться после просмотра",\n'
        '  "slides": [\n'
        "    {\n"
        '      "order": 1,\n'
        '      "title": "string — заголовок-тезис, не рубрика",\n'
        '      "purpose": "string — зачем этот слайд в нарративе (одно предложение)",\n'
        '      "keyPoints": ["string — короткий осмысленный тезис, 5-14 слов"],\n'
        '      "visualIntent": "string — описание визуала на русском",\n'
        '      "needsImage": false,\n'
        '      "slideType": "title|text|image|bullets|conclusion",\n'
        '      "imagePrompt": "string — детальный английский prompt для генерации изображения",\n'
        '      "speakerNotes": "string — что сказать вслух (1-2 предложения)"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Входной JSON:\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )


def _content_user_text(payload: dict[str, Any]) -> str:
    style_hint = _style_hint(payload.get("basis"))
    return (
        "Преврати утверждённое оглавление в финальное содержимое слайдов. Это контент, "
        "который окажется на экране, поэтому формулировки должны быть готовы к показу.\n"
        f"Визуальный язык: {style_hint}.\n"
        "Ответ — валидный JSON-объект без Markdown, та же структура, что на входе.\n\n"
        "Каждый слайд:\n"
        "- title: финальный заголовок (можно слегка переписать, если он шаблонный)\n"
        "- purpose: 1 предложение, роль слайда в логике\n"
        "- keyPoints: МАССИВ строк. Каждая строка — самостоятельный тезис из 8-18 слов с "
        "конкретикой (цифры/имена/действия). Без вводных слов и без перечислений типа «Тезис N».\n"
        "- needsImage: bool, true только если визуал реально нужен\n"
        "- visualIntent: на русском\n"
        "- imagePrompt: на АНГЛИЙСКОМ, детально (subject, scene, style, lighting, palette)\n"
        "- speakerNotes: 1-3 предложения для докладчика\n\n"
        "Входной JSON:\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )


def _retry_user_text(payload: dict[str, Any]) -> str:
    style_hint = _style_hint(payload.get("basis"))
    return (
        "Перепиши оглавление, учитывая обратную связь пользователя. Не повторяй прошлую структуру "
        "буквально — переосмысли её там, где этого требует фидбек, остальное сохрани.\n"
        f"Визуальный язык: {style_hint}.\n"
        "Ответ — JSON в той же форме, что и обычная генерация оглавления.\n\n"
        f"Фидбек: {payload.get('feedback')}\n\n"
        "Контекст:\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )


def _style_hint(basis: Any) -> str:
    if not isinstance(basis, dict):
        return STYLE_VISUAL_LANGUAGE["business"]
    kind = basis.get("kind")
    if kind == "style":
        style_id = basis.get("styleId") or "business"
        return STYLE_VISUAL_LANGUAGE.get(style_id, STYLE_VISUAL_LANGUAGE["business"])
    return STYLE_VISUAL_LANGUAGE["business"]


# ---------------------------------------------------------------------------
# Public orchestration
# ---------------------------------------------------------------------------


def create_outline(payload: OutlineGenerationRequest) -> OutlineGenerationResponse:
    _validate_basis(payload.basis)
    outline = _mock_outline(payload) if _mock_enabled() else _generate_outline(payload)
    generation_id = _new_id("gen")
    _save_record(
        generation_id,
        {
            "id": generation_id,
            "status": "outline_ready",
            "request": payload.model_dump(mode="json"),
            "outline": outline.model_dump(mode="json"),
            "createdAt": _now_ms(),
            "updatedAt": _now_ms(),
        },
    )
    return OutlineGenerationResponse(generationId=generation_id, outline=outline)


def retry_outline(generation_id: str, payload: OutlineRetryRequest) -> OutlineGenerationResponse:
    record = _load_record(generation_id)
    source_request = OutlineGenerationRequest.model_validate(record["request"])
    _validate_basis(source_request.basis)

    if _mock_enabled():
        outline = _mock_outline(source_request, feedback=payload.feedback)
    else:
        llm_payload = {
            "task": "presentation_outline_retry",
            "prompt": source_request.prompt,
            "slideCount": source_request.slideCount,
            "language": source_request.language,
            "basis": source_request.basis.model_dump(mode="json"),
            "previousOutline": payload.outline.model_dump(mode="json"),
            "feedback": payload.feedback,
        }
        raw = _call_qwen_json(
            user_text=_retry_user_text(llm_payload),
            system_prompt=OUTLINE_SYSTEM_PROMPT,
            max_new_tokens=2200,
            temperature=0.85,
        )
        outline = _normalize_outline(raw, source_request)

    record["status"] = "outline_ready"
    record["outline"] = outline.model_dump(mode="json")
    record["updatedAt"] = _now_ms()
    _save_record(generation_id, record)
    return OutlineGenerationResponse(generationId=generation_id, outline=outline)


def build_presentation(
    generation_id: str, payload: PresentationBuildRequest
) -> PresentationDocument:
    record = _load_record(generation_id)
    if record.get("status") not in {"outline_ready", "presentation_ready"}:
        raise AiApiError(409, "Generation is not ready for presentation build")

    source_request = OutlineGenerationRequest.model_validate(record["request"])
    _validate_basis(source_request.basis)

    outline = payload.outline
    if not outline.slides:
        raise AiApiError(422, "Approved outline must contain at least one slide")

    content_generation_error: str | None = None
    if _mock_enabled():
        content_outline = _mock_content(source_request, outline)
    else:
        try:
            content_outline = _generate_slide_content(source_request, outline)
        except AiApiError as exc:
            if exc.status_code != 502:
                raise
            content_generation_error = str(exc.detail)
            logger.warning(
                "Presentation content generation failed for %s; using approved outline: %s",
                generation_id,
                exc.detail,
            )
            content_outline = _fallback_content(source_request, outline)
    doc = _build_document(source_request.basis, content_outline, payload.imagePolicy)
    if content_generation_error:
        generation_meta = (doc.meta or {}).get("generation") or {}
        doc.meta = {
            **(doc.meta or {}),
            "generation": {
                **generation_meta,
                "contentFallback": True,
                "contentFallbackReason": content_generation_error,
            },
        }
    saved = save_presentation(doc)

    if payload.imagePolicy.generateImages:
        _enqueue_image_jobs(saved, content_outline, payload.imagePolicy.imageType)

    record["status"] = "presentation_ready"
    record["approvedOutline"] = outline.model_dump(mode="json")
    record["contentOutline"] = content_outline.model_dump(mode="json")
    if content_generation_error:
        record["contentFallbackError"] = content_generation_error
    record["presentationId"] = saved.id
    record["updatedAt"] = _now_ms()
    _save_record(generation_id, record)
    return saved


# ---------------------------------------------------------------------------
# Single-slide and single-image regeneration
# ---------------------------------------------------------------------------


def regenerate_slide_content(
    presentation_id: str,
    slide_id: str,
    instructions: str | None,
) -> PresentationDocument:
    """Re-runs the LLM for a single slide, keeping the rest of the deck intact."""
    doc = get_presentation(presentation_id)
    if not doc:
        raise AiApiError(404, "Presentation not found")
    slide_index = next(
        (i for i, s in enumerate(doc.slides) if s.id == slide_id), -1
    )
    if slide_index < 0:
        raise AiApiError(404, "Slide not found")

    generation_meta = (doc.meta or {}).get("generation") or {}
    outline_data = generation_meta.get("outline") or _outline_from_document(doc)
    outline = PresentationOutline.model_validate(outline_data)
    basis_dict = generation_meta.get("basis") or _default_basis_dict()
    style_hint = _style_hint(basis_dict)

    target_outline = next(
        (s for s in outline.slides if s.order == slide_index + 1),
        None,
    ) or _outline_slide_from_doc_slide(doc.slides[slide_index], slide_index + 1)

    if _mock_enabled():
        new_slide_outline = target_outline.model_copy(
            update={
                "title": f"{target_outline.title} (rev {random.randint(2, 9)})",
                "keyPoints": [
                    f"Уточнено: {instructions[:80]}" if instructions else "Уточнённый тезис"
                ] + (target_outline.keyPoints or []),
            }
        )
    else:
        llm_payload = {
            "task": "regenerate_single_slide",
            "presentationTitle": outline.title,
            "audience": outline.audience,
            "goal": outline.goal,
            "slideIndex": slide_index + 1,
            "totalSlides": len(doc.slides),
            "currentSlide": target_outline.model_dump(mode="json"),
            "instructions": instructions or "Перепиши слайд так, чтобы формулировки стали "
            "конкретнее, добавь цифры/факты, убери штампы и канцелярит.",
            "neighbours": [
                doc.slides[idx].name or f"Слайд {idx + 1}"
                for idx in (slide_index - 1, slide_index + 1)
                if 0 <= idx < len(doc.slides)
            ],
            "styleHint": style_hint,
        }
        user_text = (
            "Перепиши ОДИН слайд презентации. Сохрани его роль в нарративе, но улучши "
            "формулировки и сделай конкретнее. Ответ — JSON-объект ровно с теми же ключами, "
            "что у currentSlide. Не возвращай массив и не возвращай весь outline.\n\n"
            f"Контекст:\n{json.dumps(llm_payload, ensure_ascii=False)}"
        )
        raw = _call_qwen_json(
            user_text=user_text,
            system_prompt=CONTENT_SYSTEM_PROMPT,
            max_new_tokens=900,
            temperature=0.9,
        )
        new_slide_outline = _normalize_single_slide(raw, target_outline, slide_index + 1)

    if not new_slide_outline.imagePrompt and (
        new_slide_outline.needsImage or new_slide_outline.slideType == "image"
    ):
        new_slide_outline = new_slide_outline.model_copy(
            update={
                "imagePrompt": _craft_image_prompt(
                    outline.title,
                    new_slide_outline,
                    style_hint,
                )
            }
        )

    _replace_slide_in_document(doc, slide_index, new_slide_outline, outline)
    saved = save_presentation(doc)

    if new_slide_outline.needsImage or new_slide_outline.slideType == "image":
        image_type = (
            (generation_meta.get("imagePolicy") or {}).get("imageType") or "png"
        )
        _enqueue_image_jobs_for_slide(saved, slide_index, new_slide_outline, image_type)

    return saved


def regenerate_slide_image(
    presentation_id: str,
    slide_id: str,
    prompt_override: str | None,
    image_type: str | None = None,
) -> dict[str, Any]:
    """Schedules a fresh image-generation job for the given slide."""
    doc = get_presentation(presentation_id)
    if not doc:
        raise AiApiError(404, "Presentation not found")
    slide_index = next(
        (i for i, s in enumerate(doc.slides) if s.id == slide_id), -1
    )
    if slide_index < 0:
        raise AiApiError(404, "Slide not found")
    slide = doc.slides[slide_index]
    image_element = next((el for el in slide.elements if el.type == "image"), None)
    if not image_element:
        raise AiApiError(422, "Slide has no image element to regenerate")

    generation_meta = (doc.meta or {}).get("generation") or {}
    style_hint = _style_hint(generation_meta.get("basis"))
    outline_data = generation_meta.get("outline") or _outline_from_document(doc)
    outline = PresentationOutline.model_validate(outline_data)
    target_outline = next(
        (s for s in outline.slides if s.order == slide_index + 1),
        None,
    ) or _outline_slide_from_doc_slide(slide, slide_index + 1)

    final_prompt = (prompt_override or "").strip()
    if not final_prompt:
        final_prompt = _craft_image_prompt(outline.title, target_outline, style_hint)

    job_image_type = (
        image_type
        or (generation_meta.get("imagePolicy") or {}).get("imageType")
        or "png"
    )

    job = _create_or_replace_job(
        presentation_id=presentation_id,
        slide_id=slide.id,
        element_id=image_element.id,
        prompt=final_prompt,
        image_type=job_image_type,
    )
    _start_worker(presentation_id, job["id"])
    return job


def get_image_jobs_status(presentation_id: str) -> dict[str, Any]:
    state = get_image_jobs(presentation_id) or {
        "presentationId": presentation_id,
        "jobs": {},
    }
    return {
        "presentationId": presentation_id,
        "jobs": list(state.get("jobs", {}).values()),
    }


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------


def _generate_outline(payload: OutlineGenerationRequest) -> PresentationOutline:
    llm_payload = {
        "task": "presentation_outline",
        "prompt": payload.prompt,
        "slideCount": payload.slideCount,
        "language": payload.language,
        "basis": payload.basis.model_dump(mode="json"),
    }
    raw = _call_qwen_json(
        user_text=_outline_user_text(llm_payload),
        system_prompt=OUTLINE_SYSTEM_PROMPT,
        max_new_tokens=2400,
        temperature=0.85,
    )
    return _normalize_outline(raw, payload)


def _generate_slide_content(
    source_request: OutlineGenerationRequest, outline: PresentationOutline
) -> PresentationOutline:
    llm_payload = {
        "task": "presentation_slide_content",
        "prompt": source_request.prompt,
        "outline": outline.model_dump(mode="json"),
        "basis": source_request.basis.model_dump(mode="json"),
    }
    raw = _call_qwen_json(
        user_text=_content_user_text(llm_payload),
        system_prompt=CONTENT_SYSTEM_PROMPT,
        max_new_tokens=4500,
        temperature=0.8,
    )
    return _normalize_outline(raw, source_request, fallback_outline=outline)


def _call_qwen_json(
    *,
    user_text: str,
    system_prompt: str,
    max_new_tokens: int,
    temperature: float = 0.7,
    top_p: float = 0.95,
    top_k: int = 60,
) -> dict[str, Any]:
    last_text = ""
    last_error: AiApiError | None = None
    # Qwen is non-deterministic and occasionally returns prose around the JSON
    # or truncates mid-object. Retry once with more headroom and a cooler
    # temperature before surfacing 502 to the user.
    attempts = (
        (max_new_tokens, temperature),
        (max(max_new_tokens, int(max_new_tokens * 1.4) + 200), max(0.3, temperature - 0.2)),
    )
    for attempt_index, (tokens, temp) in enumerate(attempts):
        text = _call_qwen_text(
            user_text=user_text,
            system_prompt=system_prompt,
            max_new_tokens=tokens,
            temperature=temp,
            top_p=top_p,
            top_k=top_k,
        )
        last_text = text
        try:
            return _extract_json(text)
        except AiApiError as exc:
            last_error = exc
            logger.warning(
                "Qwen JSON parse failed on attempt %d/%d: %s; response head: %s",
                attempt_index + 1,
                len(attempts),
                exc.detail,
                text[:500].replace("\n", " "),
            )
    logger.error(
        "Qwen JSON parse failed after %d attempts; full response: %s",
        len(attempts),
        last_text,
    )
    raise last_error or AiApiError(502, "Qwen response is not valid JSON")


def _call_qwen_text(
    *,
    user_text: str,
    system_prompt: str,
    max_new_tokens: int,
    temperature: float = 0.7,
    top_p: float = 0.95,
    top_k: int = 60,
) -> str:
    token = os.getenv("RT_AI_TOKEN")
    if not token:
        raise AiApiError(401, "RT_AI_TOKEN is not configured")

    base_url = os.getenv("RT_AI_BASE_URL", "https://ai.rt.ru/api/1.0").rstrip("/")
    model = os.getenv("RT_AI_LLM_MODEL", "Qwen/Qwen2.5-72B-Instruct")
    timeout = float(os.getenv("RT_AI_TIMEOUT_SECONDS", "120"))
    body = {
        "uuid": str(uuid.uuid4()),
        "chat": {
            "model": model,
            "user_message": user_text,
            "contents": [{"type": "text", "text": user_text}],
            "message_template": "<s>{role}\n{content}</s>",
            "response_template": "<s>bot\n",
            "system_prompt": system_prompt,
            "max_new_tokens": max_new_tokens,
            "no_repeat_ngram_size": 5,
            "repetition_penalty": 1.18,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "chat_history": [],
        },
    }
    data = _request_json(
        f"{base_url}/llama/chat",
        "POST",
        token,
        json.dumps(body, ensure_ascii=False).encode("utf-8"),
        timeout,
    )
    try:
        return data[0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AiApiError(502, "Qwen response does not contain message.content") from exc


def _request_json(
    url: str, method: str, token: str, data: bytes | None, timeout: float
) -> Any:
    req = request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        external_detail = _read_http_error(exc)
        if exc.code in {401, 403}:
            raise AiApiError(
                401,
                f"External AI service rejected RT_AI_TOKEN: {external_detail}",
            ) from exc
        raise AiApiError(
            502,
            f"External AI service returned HTTP {exc.code}: {external_detail}",
        ) from exc
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise AiApiError(502, f"External AI service request failed: {exc}") from exc


def _read_http_error(exc: error.HTTPError) -> str:
    try:
        body = exc.read(2000).decode("utf-8", "replace").strip()
    except Exception:
        body = ""
    return body or exc.reason or "empty response body"


def _extract_json(text: str) -> dict[str, Any]:
    candidates: list[str] = []

    def _push(s: str) -> None:
        s = s.strip()
        if s and s not in candidates:
            candidates.append(s)

    _push(text)

    cleaned = text.strip()
    if cleaned.startswith("```"):
        stripped = cleaned.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:]
        _push(stripped)

    fence_match = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL | re.IGNORECASE)
    if fence_match:
        _push(fence_match.group(1))

    _push(_balanced_fragment(text, "{", "}"))
    _push(_balanced_fragment(text, "[", "]"))

    naive_obj_first = text.find("{")
    naive_obj_last = text.rfind("}")
    if naive_obj_first >= 0 and naive_obj_last > naive_obj_first:
        _push(text[naive_obj_first : naive_obj_last + 1])
    naive_arr_first = text.find("[")
    naive_arr_last = text.rfind("]")
    if naive_arr_first >= 0 and naive_arr_last > naive_arr_first:
        _push(text[naive_arr_first : naive_arr_last + 1])

    for raw in candidates:
        for variant in (raw, _strip_trailing_commas(raw), _repair_truncated(raw)):
            if not variant:
                continue
            try:
                parsed = json.loads(variant)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, list):
                return {"slides": parsed}

    raise AiApiError(502, "Qwen response is not valid JSON")


def _balanced_fragment(text: str, open_ch: str, close_ch: str) -> str:
    """Returns the substring spanning a balanced open/close pair, ignoring brackets inside strings."""
    start = text.find(open_ch)
    if start < 0:
        return ""
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return ""


def _strip_trailing_commas(text: str) -> str:
    return re.sub(r",(\s*[}\]])", r"\1", text)


def _repair_truncated(text: str) -> str:
    """Closes unbalanced braces/brackets so a truncated Qwen response can still parse."""
    if not text:
        return ""
    in_string = False
    escape = False
    stack: list[str] = []
    last_complete = -1
    for i, ch in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch in "{[":
            stack.append("}" if ch == "{" else "]")
        elif ch in "}]":
            if stack and stack[-1] == ch:
                stack.pop()
                if not stack:
                    last_complete = i
    if not stack:
        return text
    head = text[: last_complete + 1] if last_complete >= 0 else text
    if last_complete >= 0:
        return head
    repaired = text
    if in_string:
        repaired += '"'
    repaired = _strip_trailing_commas(repaired)
    repaired = re.sub(r"[,\s]+$", "", repaired)
    repaired += "".join(reversed(stack))
    return repaired


# ---------------------------------------------------------------------------
# Outline normalization
# ---------------------------------------------------------------------------


def _normalize_outline(
    raw: dict[str, Any],
    source_request: OutlineGenerationRequest,
    fallback_outline: PresentationOutline | None = None,
) -> PresentationOutline:
    data = raw.get("outline", raw)
    if isinstance(data, list):
        data = {"slides": data}
    if not isinstance(data, dict):
        raise AiApiError(502, "Qwen JSON must be an object")

    fallback_title = (
        fallback_outline.title
        if fallback_outline
        else _title_from_prompt(source_request.prompt)
    )
    slides_raw = data.get("slides") or []
    if not isinstance(slides_raw, list) or not slides_raw:
        raise AiApiError(502, "Qwen JSON must contain a non-empty slides array")

    slides: list[OutlineSlide] = []
    previous = {s.order: s for s in (fallback_outline.slides if fallback_outline else [])}
    for idx, item in enumerate(slides_raw, start=1):
        if not isinstance(item, dict):
            item = {"title": str(item)}
        fallback_slide = previous.get(idx)
        slides.append(
            _coerce_slide(item, idx, fallback_slide)
        )

    return PresentationOutline(
        title=str(data.get("title") or fallback_title),
        audience=data.get("audience") or (fallback_outline.audience if fallback_outline else None),
        goal=data.get("goal") or (fallback_outline.goal if fallback_outline else None),
        slides=slides[: source_request.slideCount],
    )


def _normalize_single_slide(
    raw: dict[str, Any],
    fallback: OutlineSlide,
    expected_order: int,
) -> OutlineSlide:
    if isinstance(raw, dict) and isinstance(raw.get("slide"), dict):
        raw = raw["slide"]
    if isinstance(raw, dict) and isinstance(raw.get("slides"), list) and raw["slides"]:
        raw = raw["slides"][0]
    if not isinstance(raw, dict):
        raise AiApiError(502, "Slide regeneration response must be an object")
    return _coerce_slide(raw, expected_order, fallback)


def _coerce_slide(
    item: dict[str, Any],
    idx: int,
    fallback: OutlineSlide | None,
) -> OutlineSlide:
    key_points = _coerce_str_list(
        item.get("keyPoints")
        or item.get("points")
        or item.get("bullets")
        or (fallback.keyPoints if fallback else [])
    )
    slide_type = item.get("slideType") or (fallback.slideType if fallback else None)
    if slide_type not in ALLOWED_SLIDE_TYPES:
        slide_type = None
    visual_intent = (
        item.get("visualIntent")
        or item.get("visual")
        or item.get("imageDescription")
        or (fallback.visualIntent if fallback else None)
    )
    image_prompt = (
        item.get("imagePrompt")
        or item.get("visualPrompt")
        or (fallback.imagePrompt if fallback else None)
    )
    needs_image = bool(
        item.get("needsImage")
        or item.get("needImage")
        or slide_type == "image"
        or (fallback.needsImage if fallback else False)
    )
    return OutlineSlide(
        order=int(item.get("order") or idx),
        title=str(item.get("title") or (fallback.title if fallback else f"Слайд {idx}")),
        purpose=str(item.get("purpose") or (fallback.purpose if fallback else "")),
        keyPoints=key_points,
        visualIntent=str(visual_intent) if visual_intent else None,
        needsImage=needs_image,
        slideType=slide_type,
        imagePrompt=str(image_prompt) if image_prompt else None,
        speakerNotes=item.get("speakerNotes") or item.get("notes") or (fallback.speakerNotes if fallback else None),
    )


# ---------------------------------------------------------------------------
# Document assembly
# ---------------------------------------------------------------------------


def _build_document(
    basis: GenerationBasis, outline: PresentationOutline, image_policy: ImagePolicy
) -> PresentationDocument:
    if isinstance(basis, LayoutGenerationBasis):
        template = get_template(basis.templateId)
        if not template:
            raise AiApiError(422, f"Template not found: {basis.templateId}")
        doc = _build_layout_document(template, basis, outline)
    elif isinstance(basis, StyleGenerationBasis):
        doc = _build_style_document(basis, outline)
    else:
        raise AiApiError(422, "Unsupported generation basis")

    doc.meta = {
        **(doc.meta or {}),
        "generation": {
            "basis": basis.model_dump(mode="json"),
            "outline": outline.model_dump(mode="json"),
            "imagePolicy": image_policy.model_dump(mode="json"),
        },
    }
    return doc


def _build_layout_document(
    template: TemplateDocument,
    basis: LayoutGenerationBasis,
    outline: PresentationOutline,
) -> PresentationDocument:
    doc = PresentationDocument(
        schemaVersion="1.0.0",
        documentType="presentation",
        id=_new_id("pres"),
        name=outline.title,
        templateId=template.id,
        slideSize=template.slideSize.model_copy(deep=True),
        theme=template.theme.model_copy(deep=True),
        slides=[],
        assets=[a.model_copy(deep=True) for a in template.assets],
    )
    for idx, slide_outline in enumerate(outline.slides):
        layout = _pick_layout(template, basis, slide_outline, idx, len(outline.slides))
        doc.slides.append(_slide_from_layout(layout, slide_outline, outline))
    return doc


def _pick_layout(
    template: TemplateDocument,
    basis: LayoutGenerationBasis,
    slide: OutlineSlide,
    idx: int,
    total: int,
) -> LayoutDocument:
    layouts = template.layouts
    if basis.layoutIds:
        allowed = set(basis.layoutIds)
        filtered = [layout for layout in layouts if layout.id in allowed]
        if filtered:
            layouts = filtered

    wanted = slide.slideType
    if not wanted:
        if idx == 0:
            wanted = "title"
        elif idx == total - 1:
            wanted = "conclusion"
        elif slide.needsImage:
            wanted = "image"
        elif len(slide.keyPoints) >= 2:
            wanted = "bullets"
        else:
            wanted = "text"

    return (
        next((layout for layout in layouts if layout.slideType == wanted), None)
        or next((layout for layout in layouts if layout.slideType == "text"), None)
        or layouts[0]
    )


def _slide_from_layout(
    layout: LayoutDocument,
    slide_outline: OutlineSlide,
    outline: PresentationOutline,
) -> SlideDocument:
    elements: list[dict[str, Any]] = []
    for element in layout.elements:
        payload = element.model_dump(mode="json", by_alias=True)
        source_id = payload["id"]
        payload["id"] = _new_id("el")
        behavior = payload.get("contentBehavior") or {}
        fill_role = behavior.get("fillRole") or payload.get("role")
        if behavior.get("kind") == "placeholder":
            payload["sourcePlaceholderId"] = source_id
            payload["contentBehavior"] = {
                "kind": "generated",
                "readonly": False,
                "fillRole": fill_role,
            }
        if payload["type"] == "text":
            payload["text"] = _text_for_role(fill_role, slide_outline, outline)
            _apply_text_fit(payload, fill_role)
        elif payload["type"] == "image":
            payload["assetId"] = None
            prompt = (
                slide_outline.imagePrompt
                or slide_outline.visualIntent
                or slide_outline.title
            )
            payload["placeholder"] = slide_outline.visualIntent or "Картинка генерируется…"
            payload["generation"] = {
                "prompt": prompt,
                "model": _image_model_name(),
            }
            payload["meta"] = {
                **(payload.get("meta") or {}),
                "imageGeneration": {
                    "status": "pending",
                    "prompt": prompt,
                },
            }
        elements.append(payload)

    return SlideDocument.model_validate(
        {
            "id": _new_id("slide"),
            "name": slide_outline.title,
            "slideType": slide_outline.slideType or layout.slideType,
            "layoutId": layout.id,
            "background": layout.background.model_dump(mode="json", by_alias=True),
            "elements": elements,
            "notes": slide_outline.speakerNotes or slide_outline.purpose,
            "meta": {"outlineOrder": slide_outline.order},
        }
    )


def _build_style_document(
    basis: StyleGenerationBasis,
    outline: PresentationOutline,
) -> PresentationDocument:
    theme = STYLE_THEMES[basis.styleId].model_copy(deep=True)
    doc = PresentationDocument(
        schemaVersion="1.0.0",
        documentType="presentation",
        id=_new_id("pres"),
        name=outline.title,
        slideSize=SlideSize(widthEmu=12192000, heightEmu=6858000, ratio="16:9"),
        theme=theme,
        slides=[],
        assets=[],
    )
    for idx, slide_outline in enumerate(outline.slides):
        doc.slides.append(_style_slide(slide_outline, outline, theme, idx))
    return doc


def _style_slide(
    slide_outline: OutlineSlide,
    outline: PresentationOutline,
    theme: PresentationTheme,
    idx: int,
) -> SlideDocument:
    is_title = idx == 0 or slide_outline.slideType == "title"
    is_image = slide_outline.needsImage or slide_outline.slideType == "image"
    background = BackgroundColor(type="color", value=theme.colors.background)
    elements: list[dict[str, Any]] = []

    if is_title:
        elements.append(
            _text_element(
                "title",
                outline.title,
                914400, 2000000, 10363200, 1650000,
                56, 700, theme.colors.text,
            )
        )
        subtitle = slide_outline.purpose or outline.goal or outline.audience or ""
        if subtitle:
            elements.append(
                _text_element(
                    "subtitle",
                    subtitle,
                    914400, 3850000, 10363200, 900000,
                    28, 400, theme.colors.secondary,
                )
            )
    else:
        title_w = 5200000 if is_image else 10363200
        body_w = 5200000 if is_image else 10363200
        title_h = 1050000 if is_image else 950000
        body_y = 1850000 if is_image else 1750000
        body_h = 4100000 if is_image else 4300000
        elements.append(
            _text_element(
                "title",
                slide_outline.title,
                914400, 700000, title_w, title_h,
                38, 700, theme.colors.text,
            )
        )
        role = "bulletList" if slide_outline.keyPoints else "body"
        elements.append(
            _text_element(
                role,
                _text_for_role(role, slide_outline, outline),
                914400, body_y, body_w, body_h,
                24, 400, theme.colors.text,
            )
        )
        if is_image:
            elements.append(
                _image_placeholder_element(
                    slide_outline,
                    6700000, 1450000, 4572000, 4300000,
                )
            )

    return SlideDocument(
        id=_new_id("slide"),
        name=slide_outline.title,
        slideType=slide_outline.slideType or ("title" if is_title else "image" if is_image else "bullets"),
        background=background,
        elements=elements,
        notes=slide_outline.speakerNotes or slide_outline.purpose,
        meta={"outlineOrder": slide_outline.order},
    )


EMU_PER_PT = 12700

TEXT_MIN_FONT_BY_ROLE = {
    "title": 14,
    "subtitle": 12,
    "body": 11,
    "bulletList": 11,
    "caption": 9,
}
TEXT_MAX_LINES_BY_ROLE = {
    "title": 2,
    "subtitle": 3,
    "body": 10,
    "bulletList": 8,
    "caption": 3,
}
TEXT_MAX_CHARS_BY_ROLE = {
    "title": 110,
    "subtitle": 180,
    "body": 900,
    "bulletList": 700,
    "caption": 180,
}
TEXT_LINE_HEIGHT_BY_ROLE = {
    "title": 1.12,
    "subtitle": 1.22,
    "body": 1.35,
    "bulletList": 1.35,
    "caption": 1.2,
}


def _text_constraints_for_role(role: str | None) -> dict[str, Any]:
    role_key = role or "body"
    constraints = {
        "maxLines": TEXT_MAX_LINES_BY_ROLE.get(role_key, 8),
        "overflow": "shrink",
        "minFontSize": TEXT_MIN_FONT_BY_ROLE.get(role_key, 10),
    }
    max_chars = TEXT_MAX_CHARS_BY_ROLE.get(role_key)
    if max_chars:
        constraints["maxChars"] = max_chars
    if role_key == "title":
        constraints["splitStrategy"] = "none"
    return constraints


def _estimated_wrapped_lines(text: str, role: str | None, width_emu: int, font_size: int) -> int:
    role_key = role or "body"
    width_pt = max(20, width_emu / EMU_PER_PT - 8)
    avg_char_width = max(4, font_size * (0.5 if role_key in {"title", "bulletList"} else 0.47))
    chars_per_line = max(8, int(width_pt / avg_char_width))
    total = 0
    for raw_line in (text or "").splitlines() or [""]:
        line = raw_line.strip()
        if role_key == "bulletList":
            line = line.lstrip("•-* ").strip()
        total += max(1, math.ceil(max(1, len(line)) / chars_per_line))
    return total


def _fit_font_size(
    text: str,
    role: str | None,
    width_emu: int,
    height_emu: int,
    font_size: int,
    line_height: float,
    min_font_size: int,
) -> int:
    height_pt = max(8, height_emu / EMU_PER_PT - 8)
    size = font_size
    while size > min_font_size:
        lines = _estimated_wrapped_lines(text, role, width_emu, size)
        if lines * size * line_height <= height_pt:
            break
        size -= 1
    return size


def _apply_text_fit(payload: dict[str, Any], role: str | None) -> None:
    if payload.get("type") != "text":
        return
    style = payload.setdefault("style", {})
    frame = payload.get("frame") or {}
    constraints = payload.get("constraints") or {}
    defaults = _text_constraints_for_role(role)
    for key, value in defaults.items():
        if constraints.get(key) is None:
            constraints[key] = value
    payload["constraints"] = constraints

    line_height = style.get("lineHeight") or TEXT_LINE_HEIGHT_BY_ROLE.get(role or "body", 1.35)
    style["lineHeight"] = line_height
    font_size = int(style.get("fontSize") or 16)
    min_font_size = int(constraints.get("minFontSize") or defaults["minFontSize"])
    style["fontSize"] = _fit_font_size(
        payload.get("text") or "",
        role,
        int(frame.get("wEmu") or 1),
        int(frame.get("hEmu") or 1),
        font_size,
        float(line_height),
        min_font_size,
    )


def _text_element(
    role: str,
    text: str,
    x: int,
    y: int,
    w: int,
    h: int,
    font_size: int,
    font_weight: int,
    color: str,
) -> dict[str, Any]:
    line_height = TEXT_LINE_HEIGHT_BY_ROLE.get(role, 1.35)
    constraints = _text_constraints_for_role(role)
    fitted_font_size = _fit_font_size(
        text,
        role,
        w,
        h,
        font_size,
        line_height,
        constraints["minFontSize"],
    )
    return {
        "id": _new_id("el"),
        "type": "text",
        "role": role,
        "contentBehavior": {"kind": "generated", "readonly": False, "fillRole": role},
        "text": text,
        "frame": {"xEmu": x, "yEmu": y, "wEmu": w, "hEmu": h, "rotate": 0},
        "style": {
            "fontFamily": "Inter",
            "fontSize": fitted_font_size,
            "fontWeight": font_weight,
            "color": color,
            "align": "left",
            "lineHeight": line_height,
        },
        "constraints": constraints,
        "zIndex": 10,
        "locked": False,
        "visible": True,
    }


def _image_placeholder_element(
    slide: OutlineSlide,
    x: int,
    y: int,
    w: int,
    h: int,
) -> dict[str, Any]:
    prompt = slide.imagePrompt or slide.visualIntent or slide.title
    return {
        "id": _new_id("el"),
        "type": "image",
        "role": "image",
        "contentBehavior": {"kind": "generated", "readonly": False, "fillRole": "image"},
        "assetId": None,
        "fit": "cover",
        "placeholder": slide.visualIntent or "Картинка генерируется…",
        "frame": {"xEmu": x, "yEmu": y, "wEmu": w, "hEmu": h, "rotate": 0},
        "generation": {"prompt": prompt, "model": _image_model_name()},
        "meta": {"imageGeneration": {"status": "pending", "prompt": prompt}},
        "zIndex": 9,
        "locked": False,
        "visible": True,
    }


# ---------------------------------------------------------------------------
# Image generation jobs
# ---------------------------------------------------------------------------

_JOB_LOCKS: dict[str, threading.Lock] = {}
_JOB_LOCKS_GUARD = threading.Lock()


def _lock_for(presentation_id: str) -> threading.Lock:
    with _JOB_LOCKS_GUARD:
        lock = _JOB_LOCKS.get(presentation_id)
        if lock is None:
            lock = threading.Lock()
            _JOB_LOCKS[presentation_id] = lock
        return lock


def _empty_jobs_state(presentation_id: str) -> dict[str, Any]:
    return {
        "presentationId": presentation_id,
        "createdAt": _now_ms(),
        "updatedAt": _now_ms(),
        "jobs": {},
    }


def _enqueue_image_jobs(
    presentation: PresentationDocument,
    outline: PresentationOutline,
    image_type: str,
) -> None:
    pending: list[tuple[str, str, str]] = []
    with _lock_for(presentation.id):
        state = get_image_jobs(presentation.id) or _empty_jobs_state(presentation.id)
        state["presentationId"] = presentation.id
        outline_by_order = {s.order: s for s in outline.slides}
        for slide_idx, slide in enumerate(presentation.slides):
            slide_outline = outline_by_order.get(slide_idx + 1)
            if not slide_outline:
                continue
            for el in slide.elements:
                if el.type != "image":
                    continue
                meta = (el.meta or {}).get("imageGeneration") or {}
                if meta.get("status") in {"ready", "in_progress"}:
                    continue
                prompt = meta.get("prompt") or slide_outline.imagePrompt or slide_outline.title
                job = _build_job_record(
                    slide.id, el.id, prompt, image_type
                )
                state["jobs"][job["id"]] = job
                pending.append((presentation.id, job["id"], prompt))
        state["updatedAt"] = _now_ms()
        save_image_jobs(presentation.id, state)
    for presentation_id, job_id, _prompt in pending:
        _start_worker(presentation_id, job_id)


def _enqueue_image_jobs_for_slide(
    presentation: PresentationDocument,
    slide_index: int,
    slide_outline: OutlineSlide,
    image_type: str,
) -> None:
    slide = presentation.slides[slide_index]
    image_element = next((el for el in slide.elements if el.type == "image"), None)
    if not image_element:
        return
    prompt = (
        slide_outline.imagePrompt
        or (image_element.meta or {}).get("imageGeneration", {}).get("prompt")
        or slide_outline.title
    )
    _create_or_replace_job(
        presentation_id=presentation.id,
        slide_id=slide.id,
        element_id=image_element.id,
        prompt=prompt,
        image_type=image_type,
    )
    job_id = _job_key(slide.id, image_element.id)
    _start_worker(presentation.id, job_id)


def _build_job_record(
    slide_id: str, element_id: str, prompt: str, image_type: str
) -> dict[str, Any]:
    return {
        "id": _job_key(slide_id, element_id),
        "slideId": slide_id,
        "elementId": element_id,
        "prompt": prompt,
        "imageType": image_type,
        "status": "pending",
        "assetId": None,
        "url": None,
        "error": None,
        "version": 1,
        "createdAt": _now_ms(),
        "updatedAt": _now_ms(),
    }


def _create_or_replace_job(
    *,
    presentation_id: str,
    slide_id: str,
    element_id: str,
    prompt: str,
    image_type: str,
) -> dict[str, Any]:
    job_id = _job_key(slide_id, element_id)
    with _lock_for(presentation_id):
        state = get_image_jobs(presentation_id) or _empty_jobs_state(presentation_id)
        existing = state["jobs"].get(job_id)
        version = (existing.get("version") if existing else 0) + 1
        job = _build_job_record(slide_id, element_id, prompt, image_type)
        job["version"] = version
        state["jobs"][job_id] = job
        state["updatedAt"] = _now_ms()
        save_image_jobs(presentation_id, state)
        return dict(job)


def _job_key(slide_id: str, element_id: str) -> str:
    return f"{slide_id}::{element_id}"


def _start_worker(presentation_id: str, job_id: str) -> None:
    thread = threading.Thread(
        target=_run_image_job,
        args=(presentation_id, job_id),
        daemon=True,
        name=f"img-{presentation_id[:8]}-{job_id[:8]}",
    )
    thread.start()


def _update_job(
    presentation_id: str,
    job_id: str,
    expected_version: int,
    patch: dict[str, Any],
) -> bool:
    with _lock_for(presentation_id):
        state = get_image_jobs(presentation_id)
        if not state:
            return False
        current = state["jobs"].get(job_id)
        if not current or current.get("version") != expected_version:
            return False
        current.update(patch)
        current["updatedAt"] = _now_ms()
        state["updatedAt"] = _now_ms()
        save_image_jobs(presentation_id, state)
        return True


def _run_image_job(presentation_id: str, job_id: str) -> None:
    with _lock_for(presentation_id):
        state = get_image_jobs(presentation_id)
        if not state:
            return
        job = state["jobs"].get(job_id)
        if not job:
            return
        version = job["version"]
        prompt = job["prompt"]
        image_type = job["imageType"]
        job["status"] = "in_progress"
        job["updatedAt"] = _now_ms()
        save_image_jobs(presentation_id, state)

    try:
        asset = _generate_image_asset(prompt, image_type)
    except AiApiError as exc:
        _update_job(
            presentation_id,
            job_id,
            version,
            {"status": "failed", "error": str(exc.detail)},
        )
        return
    except Exception as exc:  # pragma: no cover - defensive
        _update_job(
            presentation_id,
            job_id,
            version,
            {"status": "failed", "error": str(exc)},
        )
        return

    _attach_asset_to_presentation(presentation_id, asset)
    _update_job(
        presentation_id,
        job_id,
        version,
        {
            "status": "ready",
            "assetId": asset.id,
            "url": asset.url,
            "asset": {
                "id": asset.id,
                "type": "image",
                "mimeType": asset.mimeType,
                "url": asset.url,
                "fileName": asset.fileName,
            },
            "error": None,
        },
    )


def _attach_asset_to_presentation(presentation_id: str, asset: Asset) -> None:
    """Adds the new asset to the presentation document so it survives reloads.

    The frontend is the source of truth for slide-element wiring; this only
    ensures the asset is registered in `doc.assets` and visible via the static
    file route.
    """
    with _lock_for(presentation_id):
        doc = get_presentation(presentation_id)
        if not doc:
            return
        if any(a.id == asset.id for a in doc.assets):
            return
        doc.assets.append(asset)
        save_presentation(doc)


# ---------------------------------------------------------------------------
# Image generation providers (synchronous, run on worker threads)
# ---------------------------------------------------------------------------


YANDEX_ASPECTS = {"1:1", "16:9", "9:16", "3:2", "2:3", "4:7", "7:4"}


def _image_provider() -> str:
    return os.getenv("RT_AI_IMAGE_PROVIDER", "yandex").strip().lower() or "yandex"


def _image_model_name() -> str:
    if _image_provider() == "sd":
        return "stable-diffusion"
    return os.getenv("RT_AI_YANDEX_MODEL", "yandex-art")


def _generate_image_asset(prompt: str, image_type: str) -> Asset:
    if _mock_enabled():
        asset = store_asset(MOCK_IMAGE_PNG, f"generated_{uuid.uuid4().hex[:8]}.png", "image/png")
        asset.meta = {"mock": True, "prompt": prompt}
        return asset

    provider = _image_provider()
    if provider == "sd":
        return _generate_image_sd(prompt, image_type)
    return _generate_image_yandex(prompt, image_type)


def _generate_image_yandex(prompt: str, image_type: str) -> Asset:
    token = os.getenv("RT_AI_TOKEN")
    if not token:
        raise AiApiError(401, "RT_AI_TOKEN is not configured")

    base_url = os.getenv("RT_AI_BASE_URL", "https://ai.rt.ru/api/1.0").rstrip("/")
    timeout = float(os.getenv("RT_AI_TIMEOUT_SECONDS", "180"))
    aspect = os.getenv("RT_AI_YANDEX_ASPECT", "16:9").strip()
    if aspect not in YANDEX_ASPECTS:
        aspect = "16:9"
    body = {
        "uuid": str(uuid.uuid4()),
        "image": {
            "request": prompt,
            "seed": random.randint(1, 2147483647),
            "translate": _looks_like_russian(prompt),
            "model": os.getenv("RT_AI_YANDEX_MODEL", "yandex-art"),
            "aspect": aspect,
        },
    }
    response_payload = _request_json(
        f"{base_url}/ya/image",
        "POST",
        token,
        json.dumps(body, ensure_ascii=False).encode("utf-8"),
        timeout,
    )
    try:
        message_id = response_payload[0]["message"]["id"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AiApiError(502, "Yandex ART response does not contain message.id") from exc

    file_bytes = _download_image(base_url, token, "yaArt", message_id, image_type, timeout)
    mime_type = "image/jpeg" if image_type == "jpeg" else f"image/{image_type}"
    asset = store_asset(file_bytes, f"generated_{message_id}.{image_type}", mime_type)
    asset.meta = {
        "prompt": prompt,
        "externalMessageId": message_id,
        "provider": "yandex-art",
    }
    return asset


def _generate_image_sd(prompt: str, image_type: str) -> Asset:
    token = os.getenv("RT_AI_TOKEN")
    if not token:
        raise AiApiError(401, "RT_AI_TOKEN is not configured")

    base_url = os.getenv("RT_AI_BASE_URL", "https://ai.rt.ru/api/1.0").rstrip("/")
    timeout = float(os.getenv("RT_AI_TIMEOUT_SECONDS", "180"))
    body = {
        "uuid": str(uuid.uuid4()),
        "sdImage": {
            "request": prompt,
            "seed": random.randint(1, 2147483647),
            "translate": _looks_like_russian(prompt),
        },
    }
    response_payload = _request_json(
        f"{base_url}/sd/img",
        "POST",
        token,
        json.dumps(body, ensure_ascii=False).encode("utf-8"),
        timeout,
    )
    try:
        message_id = response_payload[0]["message"]["id"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AiApiError(502, "Stable Diffusion response does not contain message.id") from exc

    file_bytes = _download_image(base_url, token, "sd", message_id, image_type, timeout)
    mime_type = "image/jpeg" if image_type == "jpeg" else f"image/{image_type}"
    asset = store_asset(file_bytes, f"generated_{message_id}.{image_type}", mime_type)
    asset.meta = {
        "prompt": prompt,
        "externalMessageId": message_id,
        "provider": "stable-diffusion",
    }
    return asset


def _download_image(
    base_url: str,
    token: str,
    service_type: str,
    message_id: Any,
    image_type: str,
    timeout: float,
) -> bytes:
    query = parse.urlencode(
        {"id": message_id, "serviceType": service_type, "imageType": image_type}
    )
    req = request.Request(
        f"{base_url}/download?{query}",
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except error.HTTPError as exc:
        if exc.code in {401, 403}:
            raise AiApiError(401, "External AI service rejected RT_AI_TOKEN") from exc
        raise AiApiError(502, f"Image download returned HTTP {exc.code}") from exc
    except (error.URLError, TimeoutError) as exc:
        raise AiApiError(502, f"Image download failed: {exc}") from exc


def _looks_like_russian(text: str) -> bool:
    return any("а" <= ch.lower() <= "я" for ch in text)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _craft_image_prompt(
    presentation_title: str,
    slide: OutlineSlide,
    style_hint: str,
) -> str:
    if _mock_enabled():
        return f"{slide.title} — illustrative concept for {presentation_title}"
    summary = "; ".join((slide.keyPoints or [])[:3]) or slide.purpose or slide.title
    user_text = (
        "Create an image-generation prompt (one line, no JSON) for the following slide.\n\n"
        f"Presentation: {presentation_title}\n"
        f"Slide title: {slide.title}\n"
        f"Slide intent: {slide.purpose or '-'}\n"
        f"Key ideas: {summary}\n"
        f"Visual intent (Russian, optional): {slide.visualIntent or '-'}\n"
        f"Visual style guidance: {style_hint}\n"
        "Important: no text, captions, logos, watermarks. Subject-led, photographic or "
        "tasteful illustration, cinematic composition."
    )
    try:
        text = _call_qwen_text(
            user_text=user_text,
            system_prompt=IMAGE_PROMPT_SYSTEM,
            max_new_tokens=220,
            temperature=0.85,
            top_p=0.95,
        )
    except AiApiError:
        return f"{slide.title} — {style_hint}, no text, no logos"
    return text.strip().strip('"').strip("`").splitlines()[0].strip() or slide.title


def _replace_slide_in_document(
    doc: PresentationDocument,
    slide_index: int,
    new_outline: OutlineSlide,
    full_outline: PresentationOutline,
) -> None:
    """Replaces a slide's text and refreshes its image-generation metadata in place."""
    slide = doc.slides[slide_index]
    slide.name = new_outline.title
    slide.notes = new_outline.speakerNotes or new_outline.purpose
    slide.meta = {**(slide.meta or {}), "outlineOrder": new_outline.order}
    for el in slide.elements:
        if el.type == "text":
            role = (el.contentBehavior.fillRole if el.contentBehavior else None) or el.role
            el.text = _text_for_role(role, new_outline, full_outline)
        elif el.type == "image":
            prompt = new_outline.imagePrompt or new_outline.visualIntent or new_outline.title
            el.assetId = None
            el.placeholder = new_outline.visualIntent or "Картинка генерируется…"
            el.generation = {"prompt": prompt, "model": _image_model_name()}
            el.meta = {
                **(el.meta or {}),
                "imageGeneration": {"status": "pending", "prompt": prompt},
            }

    generation = (doc.meta or {}).get("generation") or {}
    outline_data = generation.get("outline") or full_outline.model_dump(mode="json")
    if isinstance(outline_data, dict):
        slides = list(outline_data.get("slides") or [])
        replaced = new_outline.model_dump(mode="json")
        for i, item in enumerate(slides):
            if int(item.get("order") or i + 1) == new_outline.order:
                slides[i] = replaced
                break
        else:
            slides.append(replaced)
        outline_data["slides"] = slides
    doc.meta = {
        **(doc.meta or {}),
        "generation": {**generation, "outline": outline_data},
    }


def _outline_from_document(doc: PresentationDocument) -> dict[str, Any]:
    return {
        "title": doc.name,
        "audience": None,
        "goal": None,
        "slides": [
            _outline_slide_from_doc_slide(slide, idx + 1).model_dump(mode="json")
            for idx, slide in enumerate(doc.slides)
        ],
    }


def _outline_slide_from_doc_slide(slide: SlideDocument, order: int) -> OutlineSlide:
    title = ""
    body_lines: list[str] = []
    image_prompt: str | None = None
    visual_intent: str | None = None
    needs_image = False
    for el in slide.elements:
        if el.type == "text":
            role = (el.contentBehavior.fillRole if el.contentBehavior else None) or el.role
            text = (el.text or "").strip()
            if not text:
                continue
            if role == "title" and not title:
                title = text
            elif role == "bulletList":
                body_lines.extend(line.strip("•- ").strip() for line in text.splitlines() if line.strip())
            else:
                body_lines.extend(line.strip() for line in text.splitlines() if line.strip())
        elif el.type == "image":
            needs_image = True
            gen = el.generation
            if gen and gen.prompt:
                image_prompt = gen.prompt
    return OutlineSlide(
        order=order,
        title=title or slide.name or f"Слайд {order}",
        purpose="",
        keyPoints=[line for line in body_lines if line],
        visualIntent=visual_intent,
        needsImage=needs_image,
        slideType=slide.slideType,
        imagePrompt=image_prompt,
        speakerNotes=slide.notes,
    )


def _default_basis_dict() -> dict[str, Any]:
    return {"kind": "style", "styleId": "business"}


def _text_for_role(
    role: str | None, slide: OutlineSlide, outline: PresentationOutline
) -> str:
    if role == "title":
        return slide.title
    if role == "subtitle":
        return slide.purpose or outline.goal or outline.audience or ""
    if role == "bulletList":
        points = slide.keyPoints or ([slide.purpose] if slide.purpose else [])
        return "\n".join(f"• {point}" for point in points)
    if role == "caption":
        return slide.visualIntent or ""
    if role == "slideNumber":
        return str(slide.order)

    parts: list[str] = []
    if slide.purpose:
        parts.append(slide.purpose)
    if slide.keyPoints:
        parts.extend(f"• {point}" for point in slide.keyPoints)
    return "\n".join(parts) or slide.title


def _validate_basis(basis: GenerationBasis) -> None:
    if isinstance(basis, LayoutGenerationBasis):
        template = get_template(basis.templateId)
        if not template:
            raise AiApiError(422, f"Template not found: {basis.templateId}")
        if basis.layoutIds:
            known = {layout.id for layout in template.layouts}
            unknown = [layout_id for layout_id in basis.layoutIds if layout_id not in known]
            if unknown:
                raise AiApiError(422, {"unknownLayoutIds": unknown})
    elif isinstance(basis, StyleGenerationBasis):
        if basis.styleId not in STYLE_THEMES:
            raise AiApiError(422, f"Unknown styleId: {basis.styleId}")


def _mock_outline(
    payload: OutlineGenerationRequest, feedback: str | None = None
) -> PresentationOutline:
    title = _title_from_prompt(payload.prompt)
    slides: list[OutlineSlide] = []
    for idx in range(1, payload.slideCount + 1):
        if idx == 1:
            slide_type = "title"
            slide_title = title
            points = [
                "Контекст рынка и почему сейчас удачный момент",
                "Что обещаем команде/инвесторам в результате",
            ]
        elif idx == payload.slideCount:
            slide_type = "conclusion"
            slide_title = "Что мы предлагаем сделать на следующей неделе"
            points = ["Главное решение, которое нужно принять", "Конкретный следующий шаг"]
        elif idx % 4 == 0:
            slide_type = "image"
            slide_title = f"Иллюстрация ключевой метафоры #{idx}"
            points = ["Визуальная метафора, которая закрепляет идею", "Один сильный поддерживающий тезис"]
        else:
            slide_type = "bullets"
            slide_title = f"Основной аргумент #{idx} в пользу темы"
            points = [
                "Цифра/факт #1, доказывающий аргумент",
                "Цифра/факт #2, развивающий мысль",
                "Импликация для команды",
            ]
        if feedback:
            points.append(f"Учтено: {feedback[:80]}")
        slides.append(
            OutlineSlide(
                order=idx,
                title=slide_title,
                purpose=f"Развить идею: {title}",
                keyPoints=points,
                visualIntent=f"Визуал по теме: {slide_title}",
                needsImage=slide_type == "image",
                slideType=slide_type,
                imagePrompt=(
                    f"editorial photography illustrating the idea of {slide_title}, "
                    "no text, cinematic lighting, premium B2B feel"
                ),
            )
        )
    return PresentationOutline(
        title=title,
        audience="Целевая аудитория из запроса",
        goal="Принять конкретное решение по теме",
        slides=slides,
    )


def _mock_content(
    source_request: OutlineGenerationRequest, outline: PresentationOutline
) -> PresentationOutline:
    return _fallback_content(source_request, outline)


def _fallback_content(
    source_request: OutlineGenerationRequest, outline: PresentationOutline
) -> PresentationOutline:
    slides: list[OutlineSlide] = []
    for slide in outline.slides:
        points = slide.keyPoints or [
            f"Связать с запросом: {source_request.prompt[:80]}",
            "Сформулировать вывод коротко",
        ]
        slides.append(slide.model_copy(update={"keyPoints": points}))
    return outline.model_copy(update={"slides": slides})


def _coerce_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [line.strip(" -•") for line in value.splitlines() if line.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value)]


def _title_from_prompt(prompt: str) -> str:
    first_line = prompt.splitlines()[0].strip()
    title = first_line.split(".")[0].strip()
    return title[:80] or "Новая презентация"


def _mock_enabled() -> bool:
    return os.getenv("RT_AI_MOCK", "").lower() in {"1", "true", "yes", "on"}


def _load_record(generation_id: str) -> dict[str, Any]:
    record = get_generation(generation_id)
    if not record:
        raise AiApiError(404, "Generation not found")
    return record


def _save_record(generation_id: str, record: dict[str, Any]) -> None:
    try:
        save_generation(generation_id, record)
    except ValidationError as exc:
        raise AiApiError(500, str(exc)) from exc


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _now_ms() -> int:
    return int(time.time() * 1000)


def cleanup_jobs_for_presentation(presentation_id: str) -> None:
    delete_image_jobs(presentation_id)
