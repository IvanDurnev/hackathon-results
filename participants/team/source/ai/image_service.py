import os
import time
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

RT_API_BASE = os.getenv("RT_API_BASE", "https://ai.rt.ru/api/1.0")
RT_TOKEN = os.getenv("RT_API_TOKEN", "")
IMG_MODEL = os.getenv("IMG_MODEL", "yandex-art")
IMG_ASPECT = os.getenv("IMG_ASPECT", "16:9")

def generate_image(prompt: str, save_path: str, aspect: str = None) -> str:
    if aspect is None:
        aspect = IMG_ASPECT
    
    if not RT_TOKEN or not RT_TOKEN.strip():
        print(f"⚠️ Демо: картинка не сгенерирована (нет токена)")
        return ""
    
    if not prompt or not prompt.strip():
        return ""
    
    print(f"🎨 Запрос на генерацию: '{prompt[:50]}...'")
    
    try:
        # 1. Отправка задания на генерацию
        payload = {
            "uuid": str(uuid.uuid4()),
            "image": {
                "request": prompt.strip(),
                "model": IMG_MODEL,
                "aspect": aspect,
                "translate": True # Включаем автоперевод, Yandex ART лучше понимает английский
            }
        }
        
        headers = {
            "Authorization": f"Bearer {RT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        resp = requests.post(f"{RT_API_BASE}/ya/image", headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()

        # Извлекаем task_id (учитываем, что может прийти список)
        task_id = None
        try:
            if isinstance(result, list) and len(result) > 0:
                # В твоем логе ID лежит именно здесь: result[0]['message']['id']
                task_id = result[0].get("message", {}).get("id") or result[0].get("id")
            elif isinstance(result, dict):
                task_id = result.get("message", {}).get("id") or result.get("id")
        except Exception as e:
            print(f"⚠️ Ошибка при разборе ID: {e}")

        if not task_id:
            print(f"❌ Ошибка: API не вернуло ID задачи. Ответ: {result}")
            return ""
        
        print(f"⏳ Ожидание картинки (ID: {task_id})...")

        # 2. Опрос готовности
        for attempt in range(30): # 30 попыток по 3 секунды = 90 секунд
            time.sleep(3)
            download_url = f"{RT_API_BASE}/download?id={task_id}&serviceType=yaArt&imageType=png"
            
            try:
                img_resp = requests.get(download_url, headers=headers, timeout=15)
                
                # Если 200 — значит готово и скачалось
                if img_resp.status_code == 200:
                    if len(img_resp.content) > 1000: # Проверка, что это не пустой файл
                        with open(save_path, "wb") as f:
                            f.write(img_resp.content)
                        print(f"✅ Картинка готова и сохранена: {save_path}")
                        return save_path
                
                # Если 202 или 404 — значит еще в процессе
                elif img_resp.status_code in [202, 404]:
                    continue
                else:
                    print(f"ℹ️ Статус ожидания: {img_resp.status_code}")
                    
            except Exception as e:
                continue
        
        print("⏱ Таймаут: Yandex ART не успел сгенерировать за 90 сек.")
        return ""
        
    except Exception as e:
        print(f"❌ Ошибка в generate_image: {e}")
        return ""

def get_available_aspects():
    return ["16:9", "4:3", "1:1", "9:16"]