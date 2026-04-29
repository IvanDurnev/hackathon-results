import os
import json
import uuid
from typing import Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("ROSTELECOM_API_TOKEN")
API_URL = "https://ai.rt.ru/api/1.0/llama/chat"


def get_style_prompt(style: str, tone: str) -> str:
    """Генерирует промпт для LLM на основе выбранного стиля"""

    style_guidelines = {
        "corporate": """
СТИЛЬ: Корпоративный
- Используй профессиональную, деловую лексику
- Структурируй информацию с помощью списков и подзаголовков
- Акцент на фактах, цифрах, KPI
- Тон: уверенный, экспертный
- Примеры формулировок: "Наша стратегия включает...", "Ключевые показатели эффективности..."
""",
        "creative": """
СТИЛЬ: Креативный
- Используй яркие метафоры и образные выражения
- Применяй нестандартные формулировки и риторические вопросы
- Добавляй элементы сторителлинга
- Тон: вдохновляющий, энергичный
- Примеры формулировок: "Представьте мир, где...", "Что если мы взглянем с другой стороны..."
""",
        "minimal": """
СТИЛЬ: Минималистичный
- Используй короткие, ёмкие фразы
- Избегай воды и лишних деталей
- Каждое предложение должно нести максимум смысла
- Тон: лаконичный, точный
- Примеры формулировок: "Вот факты.", "Результат: +35%", "Три шага к успеху."
"""
    }

    tone_guidelines = {
        "professional": "Используй официально-деловой стиль, избегай разговорных выражений",
        "friendly": "Будь дружелюбным и доступным, используй местоимение 'мы'",
        "academic": "Будь наставником, объясняй сложные вещи простым языком"
    }

    style_text = style_guidelines.get(style, style_guidelines["corporate"])
    tone_text = tone_guidelines.get(tone, "Будь профессиональным и убедительным")

    return f"""
{style_text}

ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ К ТОНУ: {tone_text}

ВАЖНО:
1. Для креативного стиля: добавляй по 1-2 риторических вопроса на слайд
2. Для минималистичного: каждый слайд должен быть не более 50 слов
3. Для корпоративного: используй подзаголовки и маркированные списки
"""


def generate_structure(
        prompt: str,
        doc_text: str,
        num_slides: int,
        style: str,
        tone: str
) -> Optional[list[Any]]:
    """
    Генерация структуры презентации через LLM API Ростелекома
    """

    # Получаем промпт для стиля
    style_prompt = get_style_prompt(style, tone)

    # Формируем контекст с учётом документа
    if doc_text and len(doc_text) > 0:
        prompt_with_context = (
            f"Тема презентации: {prompt}\n\n"
            f"Используй этот документ как источник информации:\n{doc_text[:1500]}"
        )
    else:
        prompt_with_context = f"Тема презентации: {prompt}"

    # Используем f-string без .format(), чтобы избежать конфликта с фигурными скобками JSON
    system_prompt = f"""Ты — профессиональный автор презентаций с 10-летним опытом.
Твоя задача — написать текст презентации в виде JSON структуры на тему {prompt}

{style_prompt}

ФОРМАТ ОТВЕТА:
Верни ТОЛЬКО валидный JSON-массив слайдов. Без markdown, без дополнительного текста.

ФОРМАТ КАЖДОГО СЛАЙДА:
{{
  "title": "Заголовок слайда (5-8 слов)",
  "content": "Основной текст слайда. Может содержать переносы строк. Для корпоративного стиля используй маркированные списки через \\n- пункт. Для креативного - добавляй вопросы. Для минималистичного - короткие фразы.",
  "image_prompt": "Запрос для генерации изображения (на русском или английском)"
}}

Создай ровно {num_slides} слайдов.
Слайды должны логически вытекать один из другого, создавая цельную историю."""

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }


    payload = {
        "uuid": str(uuid.uuid4()),
        "chat": {
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "user_message": prompt_with_context,
            "contents": [
                {
                    "type": "text",
                    "text": system_prompt,
                    "isUrl": False,
                    "isAudioAsUrl": False,
                    "idFile": 0,
                    "fileName": "",
                    "image_url": None,
                    "audio_url": None,
                    "input_audio": None
                }
            ],
            "message_template": "<s>{{role}}\n{{content}}</s>",
            "response_template": "<s>bot\n",
            "system_prompt": "Ты - эксперт по созданию презентаций. Строго следуй инструкциям пользователя.",
            "max_new_tokens": 4000,
            "no_repeat_ngram_size": 15,
            "repetition_penalty": 1.1,
            "temperature": 0.4,
            "top_k": 40,
            "top_p": 0.9,
            "chat_history": []
        }
    }

    try:
        print(f"⚡ Отправка запроса к LLM (стиль: {style}, тон: {tone})...")
        print(f"📝 Тема: {prompt[:100]}...")

        response = requests.post(API_URL, headers=headers, json=payload, timeout=180)
        response.raise_for_status()

        data = response.json()

        # Безопасный парсинг ответа
        if isinstance(data, list):
            raw_text = data[0].get("message", {}).get("content", "")
        else:
            raw_text = data.get("message", {}).get("content", "")

        if not raw_text:
            raise ValueError("Пустой ответ от модели")

        # Очистка от markdown
        raw_text = (
            raw_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        print(f"📄 Получен ответ от LLM (первые 200 символов):\n{raw_text[:200]}...")

        structure = json.loads(raw_text)

        if not isinstance(structure, list):
            raise ValueError("LLM вернул не список")

        print(f"✅ Успешно сгенерировано {len(structure)} слайдов в стиле {style}")

        return structure[:num_slides]

    except json.JSONDecodeError as e:
        print(f"❌ Ошибка JSON парсинга: {e}")
        print(f"Ответ модели (первые 500 символов):\n{raw_text[:500] if 'raw_text' in locals() else 'Нет ответа'}")
        return None

    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Статус: {e.response.status_code}")
            print(f"Ответ сервера: {e.response.text[:500]}")
        return None