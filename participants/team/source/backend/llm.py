# backend/llm.py
import json
import uuid
import logging
import re
from typing import List, Dict, Literal

import httpx
import tiktoken
from .config import (
    RT_API_BASE,
    LLM_MODEL,
    AUTH_HEADERS,
    MAX_TOKENS,
)

# ----------------------------------------------------------------------
# Логгер
# ----------------------------------------------------------------------
logger = logging.getLogger("ai-ppt-generator")

# ----------------------------------------------------------------------
# Промпт‑шаблоны (УСИЛЕННЫЕ)
# ----------------------------------------------------------------------
SYSTEM_PROMPT = """Ты — генератор структур презентаций. 
Твоя единственная задача — вернуть JSON массив слайдов.
НЕ пиши приветствий, НЕ объясняй, НЕ добавляй текст до или после JSON.
Только JSON массив."""

USER_PROMPT_TEMPLATE = """Создай структуру презентации из {max_slides} слайдов.

Тема: {user_prompt}

Документ для анализа:
{doc_excerpt}

Тон: {tone}

Верни ТОЛЬКО JSON массив в этом формате:
[
  {{
    "title": "Заголовок слайда",
    "bullets": ["Пункт 1", "Пункт 2", "Пункт 3"],
    "image_prompt": "Описание для генерации картинки (опционально)"
  }}
]

ВАЖНО: Никакого текста до или после JSON. Только массив."""


# ----------------------------------------------------------------------
# Вспомогательная функция: обрезка текста по токенам
# ----------------------------------------------------------------------
def _truncate(text: str, max_tokens: int = MAX_TOKENS) -> str:
    try:
        enc = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens = enc.encode(text)
        if len(tokens) <= max_tokens:
            return text
        truncated = enc.decode(tokens[:max_tokens])
        logger.info(f"Текст обрезан до {max_tokens} токенов")
        return truncated
    except Exception:
        limit = max_tokens * 4
        return text[:limit]


async def summarize_to_structure(
    raw_text: str,
    user_prompt: str = "",
    max_slides: int = 6,
    tone: Literal["formal", "casual", "friendly", "sales"] = "formal",
) -> List[Dict]:
    """
    1️⃣ Обрезаем исходный текст.
    2️⃣ Формируем payload, отправляем в Llama‑chat.
    3️⃣ Парсим JSON‑ответ.
    4️⃣ При ошибке – используем «простой» fallback.
    """
    logger.info(f"📥 LLM запрос: raw_text={len(raw_text)} символов, prompt={user_prompt[:50] if user_prompt else 'пустой'}...")

    # ---- 1. Текстовый excerpt ----
    doc_excerpt = _truncate(raw_text) if raw_text else "(документ не предоставлен)"

    # ---- 2. Формируем payload ----
    request_uuid = str(uuid.uuid4())
    
    # Формируем пользовательский запрос с явным требованием JSON
    user_message = USER_PROMPT_TEMPLATE.format(
        user_prompt=user_prompt or "Создай презентацию",
        doc_excerpt=doc_excerpt,
        max_slides=max_slides,
        tone=tone,
    )
    
    payload = {
        "uuid": request_uuid,
        "chat": {
            "model": LLM_MODEL,
            "system_prompt": SYSTEM_PROMPT,
            "user_message": user_message,
            "contents": [
                {
                    "type": "text",
                    "text": user_message,
                    "isUrl": False,
                }
            ],
            "max_new_tokens": MAX_TOKENS,
            "temperature": 0.1,  # Снижаем для более стабильного JSON
            "top_k": 40,
            "top_p": 0.9,
        },
    }

    chat_endpoint = f"{RT_API_BASE}/llama/chat"

    async with httpx.AsyncClient(timeout=120) as client:
        try:
            resp = await client.post(chat_endpoint, json=payload, headers=AUTH_HEADERS)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"📡 LLM ответ получен")
            
            if not isinstance(data, list) or not data:
                raise ValueError("Unexpected response format from Llama")
            content_str = data[0]["message"]["content"]
            logger.info(f"📝 LLM content: {content_str[:500]}...")
        except Exception as e:
            logger.exception(f"Llama request failed: {e}")
            raise RuntimeError("LLM request error") from e

    # ---- 3. Парсим JSON ----
    slides = []
    try:
        # Пытаемся найти JSON в ответе (иногда модель добавляет текст до/после)
        json_match = re.search(r'\[.*\]', content_str, re.DOTALL)
        if json_match:
            slides = json.loads(json_match.group())
        else:
            slides = json.loads(content_str)
            
        if not isinstance(slides, list):
            raise ValueError("LLM returned not a list")
        if len(slides) == 0:
            logger.warning("⚠️ LLM вернул пустой массив слайдов!")
    except Exception as e:
        logger.warning(f"JSON‑парсинг от LLM упал ({e}); fallback‑разделение")
        # Fallback – создаём слайды из промпта
        slides = []
        for i in range(min(max_slides, 5)):
            slides.append(
                {
                    "title": f"Слайд {i + 1}: {user_prompt[:30]}" if user_prompt else f"Слайд {i + 1}",
                    "bullets": [
                        f"Пункт {j + 1} для слайда {i + 1}" for j in range(3)
                    ],
                    "image_prompt": f"Изображение для слайда {i + 1}",
                }
            )
    
    logger.info(f"✅ Итоговое количество слайдов: {len(slides)}")
    return slides
