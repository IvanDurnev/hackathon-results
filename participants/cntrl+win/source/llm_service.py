import requests
import json

TOKEN = "eyJhbGciOiJIUzM4NCJ9.eyJzY29wZXMiOlsibGxhbWEiLCJzZCIsInlhQXJ0Il0sInN1YiI6ImhhY2thdGhvbl8yNl8wNiIsImlhdCI6MTc3Njk0OTEzMCwiZXhwIjoxNzc3NjQwMzMwfQ.gyxa9WiLcIG0FBCAkL7rm_Af-9mqxFnuZREwGVI-EsSjTn9UD-6aPPiMBbg1_qQd"

URL = "https://ai.rt.ru/api/1.0/llama/chat"


def generate_presentation_content(
    prompt,
    document_text,
    slides_count,
    style,
    tone
):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    full_prompt = f"""
Создай структуру презентации.

Тема: {prompt}
Количество слайдов: {slides_count}
Стиль: {style}
Тон: {tone}

Документ:
{document_text}

Верни только JSON строго в формате:

[
    {{
        "title": "Название слайда",
        "content": "Текст слайда"
    }}
]
"""

    payload = {
        "uuid": "00000000-0000-0000-0000-000000000000",
        "chat": {
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "user_message": full_prompt,
            "contents": [
                {
                    "type": "text",
                    "text": full_prompt
                }
            ],
            "system_prompt": "Ты помогаешь создавать профессиональные презентации.",
            "max_new_tokens": 1536,
            "temperature": 0.2,
            "top_p": 0.9
        }
    }

    response = requests.post(
        URL,
        headers=headers,
        json=payload
    )

    result = response.json()

    print(result)

    try:
        content = result[0]["message"]["content"]
        return eval(content)

    except Exception as e:
        print("Ошибка LLM:", e)

        return [
            {
                "title": "Ошибка генерации",
                "content": "Не удалось получить ответ от LLM"
            }
        ]