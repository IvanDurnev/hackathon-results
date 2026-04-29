# backend/images.py
import base64
import random
import uuid
import logging
from pathlib import Path
from typing import Tuple

import httpx

from .config import (
    RT_API_BASE,
    AUTH_HEADERS,
    CACHE_DIR,
    MAX_IMAGES,
    logger,
)
from .safety import is_prompt_safe
from .utils.hash_utils import hash_prompt

# Путь к fallback‑картинке
PLACEHOLDER_IMG_PATH = Path(__file__).parent.parent.parent / "frontend" / "assets" / "placeholder.png"


def _load_placeholder() -> bytes:
    if PLACEHOLDER_IMG_PATH.is_file():
        return PLACEHOLDER_IMG_PATH.read_bytes()
    empty_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAn8B9Ue9R8YAAAAASUVORK5CYII="
    )
    return empty_png


PLACEHOLDER_BYTES = _load_placeholder()


async def generate_image(prompt: str, service: str = "sd") -> Tuple[bytes, str]:
    """
    Асинхронный генератор изображения.
    Кеш теперь учитывает модель (sd/yaArt) в имени файла.
    """
    if not is_prompt_safe(prompt):
        logger.info(f"Prompt blocked – using placeholder: {prompt[:30]}…")
        return PLACEHOLDER_BYTES, "placeholder"

    # === ИСПРАВЛЕНИЕ: Включаем модель в хеш кеша ===
    cache_key = f"{service}_{prompt}"
    h = hash_prompt(cache_key)
    cache_path = CACHE_DIR / f"{h}.png"

    if cache_path.is_file():
        logger.debug(f"Image cache hit for prompt '{prompt[:30]}…' (model: {service})")
        return cache_path.read_bytes(), h

    if len(list(CACHE_DIR.glob("*.png"))) >= MAX_IMAGES:
        logger.warning("Reached MAX_IMAGES limit – using placeholder")
        return PLACEHOLDER_BYTES, "placeholder"

    # -------------------- 1️⃣ Формируем запрос --------------------
    request_uuid = str(uuid.uuid4())
    seed = random.randint(0, 2**31 - 1)

    if service == "sd":
        endpoint = f"{RT_API_BASE}/sd/img"
        body = {
            "uuid": request_uuid,
            "sdImage": {
                "request": prompt,
                "seed": seed,
                "translate": False,
            },
        }
        service_type = "sd"
    elif service == "yaArt":
        endpoint = f"{RT_API_BASE}/ya/image"
        body = {
            "uuid": request_uuid,
            "image": {
                "request": prompt,
                "seed": seed,
                "translate": False,
                "model": "yandex-art",
                "aspect": "1:1",
            },
        }
        service_type = "yaArt"
    else:
        logger.error(f"Unsupported image service: {service}")
        return PLACEHOLDER_BYTES, "placeholder"

    async with httpx.AsyncClient(timeout=60) as client:
        # -------------------- 2️⃣ POST‑генерация --------------------
        try:
            resp = await client.post(endpoint, json=body, headers=AUTH_HEADERS)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list) or not data:
                raise ValueError("Empty response from image generation")
            img_id = data[0]["message"]["id"]
        except Exception as e:
            logger.exception(f"Image generation request failed: {e}")
            return PLACEHOLDER_BYTES, "placeholder"

        # -------------------- 3️⃣ GET‑скачивание --------------------
        download_url = f"{RT_API_BASE}/download?id={img_id}&serviceType={service_type}&imageType=png"
        try:
            dl_resp = await client.get(download_url, headers=AUTH_HEADERS)
            dl_resp.raise_for_status()
            image_bytes = dl_resp.content
        except Exception as e:
            logger.exception(f"Downloading generated image failed: {e}")
            return PLACEHOLDER_BYTES, "placeholder"

    # -------------------- 4️⃣ Кешируем --------------------
    try:
        cache_path.write_bytes(image_bytes)
        logger.info(f"Generated and cached image for prompt '{prompt[:30]}…' (model: {service})")
    except Exception as e:
        logger.exception(f"Failed to write image to cache: {e}")

    return image_bytes, h
