# backend/app.py
import pathlib
import logging
import json
from typing import List, Optional

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

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
# Конфигурация FastAPI
# ----------------------------------------------------------------------
app = FastAPI(
    title="AI PPT Generator (rt.ru API)",
    version="0.1.0",
    description="Генерация презентаций через Llama‑LLM и Stable Diffusion / Yandex ART",
)

# ----------------------------------------------------------------------
# CORS (для разработки – позволяет любому источнику обращаться к API)
# ----------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# Pydantic‑модели, которые будут возвращаться клиенту
# ----------------------------------------------------------------------
class SlideDTO(BaseModel):
    title: str
    bullets: List[str]
    image_url: Optional[str] = None


class GenerateResponse(BaseModel):
    slides: List[SlideDTO]


# ----------------------------------------------------------------------
# Эндпоинт для отдачи кеш‑изображений
# ----------------------------------------------------------------------
from .config import CACHE_DIR

@app.get("/images/{image_hash}.png")
async def serve_image(image_hash: str):
    """
    Отдаём PNG‑файл из кеша. Если файла нет – 404.
    """
    path = CACHE_DIR / f"{image_hash}.png"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path, media_type="image/png")


# ----------------------------------------------------------------------
# API‑маршрут – РЕАЛЬНАЯ ГЕНЕРАЦИЯ через LLM
# ----------------------------------------------------------------------
@app.post("/api/generate", response_model=GenerateResponse)
async def generate_presentation(
    prompt: Optional[str] = Form(None),
    slides: int = Form(..., ge=1, le=30),
    style: str = Form("corporate"),
    tone: str = Form("formal"),
    image_service: str = Form("sd"),
    file: Optional[UploadFile] = File(None),
):
    """
    1️⃣ При необходимости – читаем текст из загруженного файла.
    2️⃣ Вызываем LLM‑pipeline (summarize_to_structure) → получаем список слайдов.
    3️⃣ Для каждого `image_prompt` генерируем изображение через выбранный сервис.
    4️⃣ Возвращаем готовый JSON‑массив.
    """
    # -------------------------------------------------------------
    # Импорты (локально, чтобы избежать циклических зависимостей)
    # -------------------------------------------------------------
    from .utils.file_parser import extract_text_from_file
    from .llm import summarize_to_structure
    from .images import generate_image

    # -------------------------------------------------------------
    # 1️⃣ Вычленить текст из загруженного файла (если file передан)
    # -------------------------------------------------------------
    if file:
        file_bytes = await file.read()
        raw_text = extract_text_from_file(file_bytes, file.filename)
        logger.info(f"📄 Файл загружен: {file.filename}, {len(raw_text)} символов")
    else:
        raw_text = ""
        logger.info("📄 Файл не загружен, используем только prompt")

    # -------------------------------------------------------------
    # 2️⃣ Сформировать структуру слайдов через LLM
    # -------------------------------------------------------------
    logger.info(f"🧠 Запрос к LLM: prompt={prompt[:50] if prompt else 'пустой'}, max_slides={slides}")
    
    slides_struct = await summarize_to_structure(
        raw_text=raw_text,
        user_prompt=prompt or "",
        max_slides=slides,
        tone=tone,
    )

    logger.info(f"✅ LLM вернул слайдов: {len(slides_struct)}")

    # -------------------------------------------------------------
    # 3️⃣ Для каждого slide["image_prompt"] генерировать картинку
    # -------------------------------------------------------------
    final_slides = []
    for idx, s in enumerate(slides_struct):
        img_url = None
        if s.get("image_prompt"):
            logger.info(f"🎨 Генерируем изображение для слайда {idx + 1}: {s['image_prompt'][:30]}...")
            img_bytes, img_hash = await generate_image(
                s["image_prompt"], service=image_service
            )
            img_url = f"/images/{img_hash}.png"
            logger.info(f"✅ Изображение готово: {img_url}")
        else:
            logger.info(f"⏭️ Слайд {idx + 1} без изображения")
            
        final_slides.append(
            SlideDTO(
                title=s["title"],
                bullets=s["bullets"],
                image_url=img_url,
            )
        )

    # -------------------------------------------------------------
    # 4️⃣ Вернуть результат
    # -------------------------------------------------------------
    logger.info(f"🎉 Презентация готова: {len(final_slides)} слайдов")
    return GenerateResponse(slides=final_slides)


# ----------------------------------------------------------------------
# Эндпоинт экспорта в PPTX
# ----------------------------------------------------------------------
@app.post("/api/export/pptx")
async def export_pptx(
    presentation_data: str = Form(...),
    style: str = Form("corporate"),
):
    """
    Генерирует PPTX файл из данных презентации.
    
    presentation_data (JSON string) = {
        "title": "Заголовок",
        "slides": [
            {"title": "...", "bullets": [...], "image_url": "..."}
        ]
    }
    """
    from .pptx_service.generator import PPTXGenerator
    
    try:
        # Парсим JSON из строки
        data = json.loads(presentation_data)
        
        logger.info(f"📊 Экспорт PPTX: {len(data.get('slides', []))} слайдов, стиль={style}")
        
        engine = PPTXGenerator(style_preset=style)
        pptx_stream = engine.generate(data)
        
        return StreamingResponse(
            pptx_stream,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": "attachment; filename=presentation.pptx"}
        )
    except Exception as e:
        logger.exception(f"PPTX генерация не удалась: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации PPTX: {str(e)}")


# ----------------------------------------------------------------------
# После **всех** API‑маршрутов монтируем статические файлы
# ----------------------------------------------------------------------
frontend_path = pathlib.Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
