from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import uuid
from datetime import datetime

# Import config
from backend.app.config import config
from backend.app.models import PresentationRequest, SlideContent, Style, Tone
from backend.app.services import LLMService, ImageService, PPTXGenerator

# Validate configuration
config.validate()

# Initialize app
app = FastAPI(
    title="AI Presentation Generator - Rostelecom",
    description="Automatic presentation generation using Rostelecom AI APIs",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services with config
llm_service = LLMService(
    api_key=config.API_TOKEN,
    api_url=config.LLAMA_API_URL
)

image_service = ImageService(
    api_key=config.API_TOKEN,
    api_url=config.YANDEX_ART_API_URL
)

pptx_generator = PPTXGenerator()

# Create directories
os.makedirs(config.GENERATED_FILES_DIR, exist_ok=True)

# Store session data
presentations_store = {}


@app.post("/api/generate")
async def generate_presentation(
        prompt: str = Form(...),
        num_slides: int = Form(10, ge=1, le=20),
        style: str = Form("corporate"),
        tone: str = Form("professional"),
        include_images: bool = Form(True),
        document: Optional[UploadFile] = File(None)
):
    """Generate presentation using Rostelecom LLM and Image APIs"""

    # Check file size
    if document and document.size > config.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {config.MAX_FILE_SIZE_MB}MB"
        )

    session_id = str(uuid.uuid4())

    try:
        # Process document if provided
        document_content = ""
        if document:
            content = await document.read()
            document_content = await llm_service.process_document(content, document.filename)

        # Create request
        request = PresentationRequest(
            prompt=prompt,
            num_slides=num_slides,
            style=Style(style),
            tone=Tone(tone),
            include_images=include_images
        )

        # Generate structure with LLM
        slides = await llm_service.generate_presentation_structure(request, document_content)

        # Adjust slide count
        if len(slides) != num_slides:
            if len(slides) < num_slides:
                for i in range(len(slides), num_slides):
                    slides.append(slides[-1] if slides else SlideContent(
                        title="Дополнительный слайд",
                        content="• Содержание\n• Дополнительная информация",
                        image_prompt="Дополнительная иллюстрация"
                    ))
            else:
                slides = slides[:num_slides]

        # Generate images if requested
        if include_images:
            for i, slide in enumerate(slides):
                if slide.image_prompt:
                    image_url = await image_service.generate_image(
                        slide.image_prompt,
                        aspect=config.DEFAULT_IMAGE_ASPECT
                    )
                    slide.image_url = image_url
                    if i < len(slides) - 1:
                        import asyncio
                        await asyncio.sleep(1)

        # Generate PPTX
        pptx_content = await pptx_generator.create_presentation(
            slides,
            style,
            include_images
        )

        # Save file
        file_path = os.path.join(config.GENERATED_FILES_DIR, f"{session_id}.pptx")
        with open(file_path, "wb") as f:
            f.write(pptx_content)

        # Store session
        presentations_store[session_id] = {
            "file_path": file_path,
            "slides": slides,
            "created_at": datetime.now().isoformat()
        }

        return JSONResponse({
            "session_id": session_id,
            "file_url": f"/api/download/{session_id}",
            "slides": [
                {
                    "title": s.title,
                    "content": s.content[:200],
                    "has_image": s.image_url is not None
                }
                for s in slides
            ],
            "message": "Презентация успешно создана!"
        })

    except Exception as e:
        print(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")


@app.get("/api/download/{session_id}")
async def download_presentation(session_id: str):
    """Download generated presentation"""
    if session_id not in presentations_store:
        raise HTTPException(status_code=404, detail="Презентация не найдена")

    file_path = presentations_store[session_id]["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"presentation_{session_id}.pptx"
    )


@app.get("/api/config")
async def get_config_info():
    """Get configuration info (without sensitive data)"""
    return {
        "api_base_url": config.API_BASE_URL,
        "llama_model": config.LLAMA_MODEL,
        "max_file_size_mb": config.MAX_FILE_SIZE_MB,
        "environment": ENV,
        "available_aspects": config.DEFAULT_IMAGE_ASPECT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "llm": "Leopold (Qwen2.5-72B)",
            "image": "Yandex ART"
        },
        "timestamp": datetime.now().isoformat(),
        "environment": ENV
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD
    )