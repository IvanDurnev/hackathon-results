import os
import json
import uuid
import re
import requests

URL = "https://ai.rt.ru/api/1.0/llama/chat"


def get_token():
    """
    Берем TOKEN только из environment variables
    """
    token = os.getenv("LLM_API_TOKEN")

    if not token:
        raise ValueError(
            "LLM_API_TOKEN not found. "
            "Добавь TOKEN в .env или environment variables"
        )

    return token


def clean_json_response(text: str) -> str:
    """
    Умное извлечение JSON даже если ответ обрезан
    """

    if not text:
        return "[]"

    # Убираем markdown
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    text = text.strip()

    start = text.find("[")

    if start == -1:
        return "[]"

    json_part = text[start:]

    # Если JSON не закрыт — пытаемся починить
    if not json_part.strip().endswith("]"):
        json_part = json_part.rstrip()

        # Ищем последний завершенный объект
        last_complete = json_part.rfind("},")

        if last_complete != -1:
            json_part = json_part[:last_complete + 1]
            json_part += "\n]"
        else:
            json_part = "[]"

    return json_part


def validate_slides(slides_data):
    """
    Мягкая валидация структуры ответа
    """

    if not isinstance(slides_data, list):
        return False

    if len(slides_data) == 0:
        return False

    for slide in slides_data:
        if not isinstance(slide, dict):
            return False

        if "title" not in slide:
            return False

        if "content" not in slide:
            return False

        # Если slide_type нет — добавляем автоматически
        if "slide_type" not in slide:
            slide["slide_type"] = "bullet"

    return True


def build_prompt(
    prompt: str,
    document_text: str,
    slides_count: int,
    style: str,
    tone: str
):
    """
    NEW PRODUCTION PROMPT
    Делает не обрубки по 2 слова,
    а нормальный краткий конспект как у Gamma
    """

    document_part = (
        document_text[:4000]
        if document_text
        else "Документ не предоставлен"
    )

    return f"""
Ты профессиональный AI-ассистент для создания премиальных презентаций уровня Gamma.

Твоя задача:
создать красивую, логичную и содержательную структуру презентации
по документу и запросу пользователя.

==================================================
ТЕМА ПРЕЗЕНТАЦИИ
==================================================

{prompt}

==================================================
КОЛИЧЕСТВО СЛЙДОВ
==================================================

Ровно {slides_count} слайдов.
Не меньше.
Не больше.

==================================================
СТИЛЬ
==================================================

{style}

==================================================
ТОН
==================================================

{tone}

==================================================
DOCX / DOCUMENT CONTENT
==================================================

{document_part}

==================================================
ЧТО НУЖНО СДЕЛАТЬ
==================================================

ВАЖНО:

НЕ пиши по 2 слова.

НЕ делай обрубленные bullet points.

Нужен именно:
краткий понятный конспект,
как в хорошей consulting / investor презентации.

Каждый слайд должен:
— раскрывать мысль
— быть понятным
— выглядеть профессионально
— содержать смысл, а не набор слов

==================================================
ФОРМАТ ОТВЕТА
==================================================

Верни СТРОГО JSON массив.

Только JSON.
Без markdown.
Без ```json
Без пояснений.
Без текста вне JSON.

Формат:

[
  {{
    "title": "Название слайда",
    "content": "Полноценное краткое объяснение мысли. 2–4 осмысленных предложения или сильные bullets с содержанием.",
    "slide_type": "bullet"
  }}
]

==================================================
ДОСТУПНЫЕ slide_type
==================================================

- bullet
- image_left
- image_right
- comparison
- timeline
- big_number
- summary
- quote
- problem
- solution
- market
- team
- finance

==================================================
ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА
==================================================

1. НЕ используй:
"Спасибо за внимание" ЕСЛИ ЧЕЛОВЕК НЕ ПОПРОСИТ
НЕ вставляй полный пользовательский prompt
в title слайдов.

Выделяй главную тему и формируй
короткие профессиональные заголовки.

Title должен быть коротким:
2–5 слов максимум.

Title не должен содержать:
"Создай презентацию"
"Сделай презентацию"
или полный запрос пользователя.

2. НЕ создавай:
титульный слайд типа
"AI Generated Presentation"

3. Каждый слайд должен быть полезным

4. - 2–4 содержательных кратких объяснения
- content должен раскрывать мысль
- не пиши по 2 слова
- нужен краткий конспект, а не набор слов
- каждый слайд должен содержать полноценную мысль

5. Нужно:
кратко + профессионально + содержательно

6. Слайды должны быть логично связаны

7. Не повторяй одинаковые мысли

8. Если есть document_text —
используй именно его,
а не абстрактные шаблоны

9. Пиши как McKinsey / BCG / Gamma

10. Если пользователь указал стиль/цвет —
логически учитывай это в подаче

==================================================
ГЛАВНОЕ
==================================================

Нужна дорогая презентация уровня SaaS,
а не школьный PowerPoint.

Отвечай только JSON.
"""


def generate_presentation_content(
    prompt: str,
    document_text: str,
    slides_count: int,
    style: str,
    tone: str
) -> list:
    """
    Генерация структуры презентации через LLM
    """

    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json"
    }

    full_prompt = build_prompt(
        prompt=prompt,
        document_text=document_text,
        slides_count=slides_count,
        style=style,
        tone=tone
    )

    payload = {
        "uuid": str(uuid.uuid4()),
        "chat": {
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "user_message": full_prompt,
            "contents": [
                {
                    "type": "text",
                    "text": full_prompt
                }
            ],
            "system_prompt": (
                "Ты эксперт по созданию презентаций. "
                "Отвечай только JSON."
            ),
            "max_new_tokens": 4096,
            "temperature": 0.2,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "no_repeat_ngram_size": 15
        }
    }

    try:
        print("Отправка запроса к LLM API...")

        response = requests.post(
            URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        print(f"Статус ответа: {response.status_code}")

        response.raise_for_status()

        result = response.json()

        print(
            f"Ответ API: "
            f"{json.dumps(result, ensure_ascii=False)[:800]}"
        )

        # Извлекаем content
        if isinstance(result, list) and len(result) > 0:
            content = result[0].get("message", {}).get("content", "")
        elif isinstance(result, dict):
            content = result.get("message", {}).get("content", "")
        else:
            content = ""

        if not content:
            print("LLM вернул пустой ответ")
            return get_fallback_slides(prompt, slides_count)

        cleaned = clean_json_response(content)

        print(f"Очищенный JSON: {cleaned[:1000]}")

        slides_data = json.loads(cleaned)

        if validate_slides(slides_data):
            print("JSON успешно провалидирован")
            print(f"Слайдов: {len(slides_data)}")
            return slides_data

        print("JSON не прошел валидацию")
        return get_fallback_slides(prompt, slides_count)

    except json.JSONDecodeError as e:
        print(f"Ошибка JSON parsing: {str(e)}")
        return get_fallback_slides(prompt, slides_count)

    except requests.exceptions.Timeout:
        print("Timeout запроса к LLM API")
        return get_fallback_slides(prompt, slides_count)

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {str(e)}")
        return get_fallback_slides(prompt, slides_count)

    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")
        return get_fallback_slides(prompt, slides_count)


def get_fallback_slides(prompt: str, slides_count: int) -> list:
    """
    Fallback если LLM недоступен
    """

    templates = [
        {
            "title": "Введение",
            "content": "Обзор темы; Цели презентации; Контекст",
            "slide_type": "title"
        },
        {
            "title": "Проблематика",
            "content": "Основные вызовы; Актуальные проблемы; Почему это важно",
            "slide_type": "bullet"
        },
        {
            "title": "Анализ",
            "content": "Текущая ситуация; Данные; Сравнение подходов",
            "slide_type": "comparison"
        },
        {
            "title": "Решение",
            "content": "Предлагаемый подход; Преимущества; Практическая ценность",
            "slide_type": "image_right"
        },
        {
            "title": "Результаты",
            "content": "Ожидаемый эффект; Метрики успеха; Бизнес-ценность",
            "slide_type": "big_number"
        },
        {
            "title": "Заключение",
            "content": "Выводы; Следующие шаги; Рекомендации",
            "slide_type": "summary"
        }
    ]

    slides = []

    for i in range(slides_count):
        template = templates[min(i, len(templates) - 1)]

        slides.append({
            "title": template["title"],
            "content": template["content"],
            "slide_type": template["slide_type"]
        })

    return slides