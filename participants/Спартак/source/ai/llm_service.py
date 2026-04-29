import os
import json
import re
import uuid
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

RT_API_BASE = os.getenv("RT_API_BASE", "https://ai.rt.ru/api/1.0")
RT_TOKEN = os.getenv("RT_API_TOKEN", "")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-72B-Instruct")

SYSTEM_PROMPT = """Ты — эксперт по презентациям. 
ОТВЕЧАЙ ТОЛЬКО В ФОРМАТЕ JSON. НЕ ПИШИ ТЕКСТ ДО ИЛИ ПОСЛЕ JSON.
НЕ ИСПОЛЬЗУЙ MARKDOWN (#, **, ```).

Структура:
{
  "slides": [
    {
      "title": "Заголовок",
      "content": "Текст слайда (используй • для списков)",
      "image_prompt": "English description for AI image generator",
      "layout": "title_content"
    }
  ]
}"""

def generate_slide_structure(user_prompt: str, doc_text: str, num_slides: int, style: str, tone: str) -> dict:
    if not RT_TOKEN or not RT_TOKEN.strip():
        return {"slides": [{"title": "Демо", "content": "Укажите токен", "image_prompt": "", "layout": "title_content"}]}

    doc_context = doc_text[:3000] if doc_text else "Документ не предоставлен"
    user_message = f"ТЕМА: {user_prompt}\nСЛАЙДОВ: {num_slides}\nВЕРНИ ТОЛЬКО JSON С КЛЮЧОМ 'slides'."

    payload = {
        "uuid": str(uuid.uuid4()),
        "chat": {
            "model": LLM_MODEL,
            "user_message": user_message,
            "contents": [{"type": "text", "text": user_message}],
            "system_prompt": SYSTEM_PROMPT,
            "max_new_tokens": 2048,
            "temperature": 0.1,
            "top_p": 0.9
        }
    }
    
    headers = {"Authorization": f"Bearer {RT_TOKEN}", "Content-Type": "application/json"}

    try:
        print(f"🤖 Отправка запроса к {LLM_MODEL}...")
        r = requests.post(f"{RT_API_BASE}/llama/chat", headers=headers, json=payload, timeout=90)
        r.raise_for_status()
        
        data = r.json()

        # ШАГ 1: Исправляем обработку списка [{...}]
        res_text = ""
        if isinstance(data, list) and len(data) > 0:
            res_text = data[0].get("message", {}).get("content", "")
        elif isinstance(data, dict):
            res_text = data.get("message", {}).get("content", "") or data.get("response", "")
        
        if not res_text:
            res_text = str(data)

        # ШАГ 2: Ищем JSON внутри текста
        res_text = res_text.replace("```json", "").replace("```", "").strip()
        start = res_text.find("{")
        end = res_text.rfind("}") + 1
        
        if start == -1:
            raise ValueError("JSON не найден в тексте ответа")

        raw_json = json.loads(res_text[start:end])

        # ШАГ 3: Приводим к формату, который ждет твой Builder
        # Если модель вложила всё в "presentation", вытаскиваем
        if "presentation" in raw_json:
            raw_json = raw_json["presentation"]
            
        if "slides" not in raw_json:
            # Если ИИ выдал список слайдов без ключа
            if isinstance(raw_json, list):
                raw_json = {"slides": raw_json}
            else:
                raise ValueError("В JSON нет ключа 'slides'")

        # ШАГ 4: Исправляем content, если ИИ прислал его списком
        for slide in raw_json["slides"]:
            if isinstance(slide.get("content"), list):
                slide["content"] = "\n".join([f"• {item}" for item in slide["content"]])
            if "image_prompt" not in slide:
                slide["image_prompt"] = f"Illustration of {user_prompt}"
            if "layout" not in slide:
                slide["layout"] = "title_content"

        return raw_json

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return {"slides": [{"title": "Ошибка парсинга", "content": f"Детали: {str(e)[:100]}", "image_prompt": "", "layout": "title_content"}]}
        
    

def validate_slide_structure(slides_data: dict) -> bool:
    return isinstance(slides_data, dict) and "slides" in slides_data