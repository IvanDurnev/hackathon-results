import os
from random import randint
import time
import asyncio
import requests
import uuid
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("ROSTELECOM_API_TOKEN")
SD_URL = "https://ai.rt.ru/api/1.0/sd/img"
DOWNLOAD_URL = "https://ai.rt.ru/api/1.0/download"

def generate_image(prompt: str, save_path: str) -> str | None:
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "uuid": str(uuid.uuid4()),
        "sdImage": {
            "request": prompt,
            "seed": randint(100_000_000, 200_000_000),
            "translate": False
        }
    }

    try:
        print(f"🎨 Генерация: {prompt[:60]}...")
        
        # Шаг 1: Запрос на генерацию
        response = requests.post(SD_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ SD Error: {response.status_code}")
            return None
        
        data = response.json()
        print(f"📦 Ответ API: {data}")
        
        # 🔑 КЛЮЧЕВОЙ МОМЕНТ: извлекаем INTEGER id из message, не uuid!
        # Формат ответа: [{"message": {"id": 12345, ...}, "uuid": "..."}]
        if isinstance(data, list) and len(data) > 0:
            message = data[0].get("message", {})
            task_id = message.get("id")  # <-- INTEGER, не uuid!
        elif isinstance(data, dict):
            message = data.get("message", {})
            task_id = message.get("id")
        else:
            print("❌ Неверный формат ответа")
            return None
        
        if not task_id:
            print("❌ Не получен id из message")
            return None
        
        print(f"✅ Получен task_id: {task_id} (type: {type(task_id).__name__})")
        
        # Шаг 2: Ждём генерацию
        time.sleep(4)
        
        # Шаг 3: Скачиваем по INTEGER id
        # Важно: serviceType=sd (маленькими буквами)
        download_url = f"{DOWNLOAD_URL}?id={task_id}&serviceType=sd&imageType=png"
        print(f"📥 Download URL: {download_url}")
        
        img_response = requests.get(
            download_url,
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            timeout=60
        )
        
        if img_response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(img_response.content)
            print(f"✅ Картинка сохранена: {save_path}")
            return save_path
        else:
            print(f"❌ Download error {img_response.status_code}: {img_response.text[:200]}")
            return None
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None
        