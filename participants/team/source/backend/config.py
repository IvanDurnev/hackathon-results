import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# ----------------------------------------------------------------------
# Загрузка .env (если файла нет – берём переменные из окружения)
# ----------------------------------------------------------------------
load_dotenv()

# ----------------------------------------------------------------------
# Логгер
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s – %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ai-ppt-generator")

# ----------------------------------------------------------------------
# Конфигурация (переменные окружения)
# ----------------------------------------------------------------------
RT_API_TOKEN = os.getenv("RT_API_TOKEN")
if not RT_API_TOKEN:
    raise RuntimeError("❗️ Переменная RT_API_TOKEN не найдена в .env")

RT_API_BASE = os.getenv("RT_API_BASE", "https://ai.rt.ru/api/1.0")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-72B-Instruct")
IMAGE_SERVICE = os.getenv("IMAGE_SERVICE", "sd")   # sd | yaArt

MAX_SLIDES = int(os.getenv("MAX_SLIDES", "8"))
MAX_IMAGES = int(os.getenv("MAX_IMAGES", "30"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1500"))

CACHE_DIR = Path(os.getenv("CACHE_DIR", "./tmp/cache")).resolve()
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
# HTTP‑заголовки, которые будем использовать для всех запросов к RT‑API
# ----------------------------------------------------------------------
AUTH_HEADERS = {
    "Authorization": f"Bearer {RT_API_TOKEN}",
    "Content-Type": "application/json",
}
