"""
FastAPI приложение для AI генератора презентаций
С интеграцией QWEN API и fallback на Ollama
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import uuid
import asyncio
from datetime import datetime

# Импорт наших модулей
from document_parser import DocumentParser
from llm_qwen_analyzer import QwenLLMAnalyzer
from pptx_builder import RostelecomPPTXBuilder

app = FastAPI(
    title="AI Генератор Презентаций Ростелеком",
    description="Автоматическая генерация презентаций с помощью QWEN AI",
    version="1.0.0"
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация компонентов
parser = DocumentParser()

# Инициализация QWEN анализатора с токеном
QWEN_TOKEN = os.getenv(
    "QWEN_TOKEN",
    "eyJhbGciOiJIUzM4NCJ9.eyJzY29wZXMiOlsibGxhbWEiLCJzZCIsInlhQXJ0Il0sInN1YiI6ImhhY2thdGhvbl8yNl8wMyIsImlhdCI6MTc3Njk0OTA0NCwiZXhwIjoxNzc3NjQwMjQ0fQ.gbftSKsqE3bf6aH6DqBLKeWQW6yyk4RpAAaMxlHIHkyzioqCufFjOIgq0FioiQv9"
)

llm_analyzer = QwenLLMAnalyzer(qwen_token=QWEN_TOKEN)

# Модели данных
class TextRequest(BaseModel):
    content: str
    tone: str = "official"
    slide_count: int = 10
    include_images: bool = True
    color_scheme: str = "gradient"

class GenerationResponse(BaseModel):
    task_id: str
    status: str
    message: str

class StatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    message: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[str] = None

# Временное хранилище задач
tasks = {}


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "service": "AI Генератор Презентаций",
        "company": "Ростелеком",
        "version": "1.0.0",
        "status": "active",
        "llm_provider": "QWEN API" if llm_analyzer.qwen_available else "Ollama",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "qwen_api": "available" if llm_analyzer.qwen_available else "unavailable",
        "ollama": "configured",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/generate/text", response_model=GenerationResponse)
async def generate_from_text(request: TextRequest):
    """
    Генерация презентации из текста
    
    Args:
        content: Текст для анализа
        tone: Тон презентации (official/creative)
        slide_count: Количество слайдов (5-20)
        include_images: Генерировать ли промпты для изображений
        color_scheme: Цветовая схема (blue/purple/gradient)
    
    Returns:
        task_id для отслеживания прогресса
    """
    
    task_id = str(uuid.uuid4())
    
    # Запуск асинхронной задачи
    asyncio.create_task(
        process_generation(
            task_id=task_id,
            content=request.content,
            tone=request.tone,
            slide_count=request.slide_count,
            include_images=request.include_images,
            color_scheme=request.color_scheme
        )
    )
    
    return GenerationResponse(
        task_id=task_id,
        status="processing",
        message=f"Генерация началась. Используется: {'QWEN API' if llm_analyzer.qwen_available else 'Ollama'}"
    )


@app.post("/api/generate/file", response_model=GenerationResponse)
async def generate_from_file(
    file: UploadFile = File(...),
    tone: str = Form("official"),
    slide_count: int = Form(10),
    include_images: bool = Form(True),
    color_scheme: str = Form("gradient")
):
    """
    Генерация презентации из файла
    
    Args:
        file: Загружаемый файл (PDF, DOCX, TXT)
        tone: Тон презентации
        slide_count: Количество слайдов
        include_images: Генерировать ли изображения
        color_scheme: Цветовая схема
    
    Returns:
        task_id для отслеживания прогресса
    """
    
    # Проверка типа файла
    allowed_extensions = ['.pdf', '.docx', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}"
        )
    
    # Сохранение файла
    upload_dir = "/tmp/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
    
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {str(e)}")
    
    # Парсинг файла
    try:
        content = parser.parse(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Ошибка парсинга файла: {str(e)}")
    finally:
        # Удаляем файл после парсинга
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Генерация
    task_id = str(uuid.uuid4())
    asyncio.create_task(
        process_generation(
            task_id=task_id,
            content=content,
            tone=tone,
            slide_count=slide_count,
            include_images=include_images,
            color_scheme=color_scheme
        )
    )
    
    return GenerationResponse(
        task_id=task_id,
        status="processing",
        message=f"Файл обработан. Генерация началась через {'QWEN API' if llm_analyzer.qwen_available else 'Ollama'}"
    )


async def process_generation(
    task_id: str,
    content: str,
    tone: str,
    slide_count: int,
    include_images: bool,
    color_scheme: str = "gradient"
):
    """
    Фоновая обработка генерации презентации
    
    Args:
        task_id: ID задачи
        content: Текст для анализа
        tone: Тон презентации
        slide_count: Количество слайдов
        include_images: Генерировать ли изображения
        color_scheme: Цветовая схема
    """
    
    try:
        # Шаг 1: Парсинг (уже сделан)
        tasks[task_id] = {
            "status": "parsing",
            "progress": 10,
            "message": "Обработка текста..."
        }
        await asyncio.sleep(0.5)
        
        # Шаг 2: Анализ с LLM (QWEN или Ollama)
        tasks[task_id] = {
            "status": "analyzing",
            "progress": 20,
            "message": f"AI анализ контента через {'QWEN API' if llm_analyzer.qwen_available else 'Ollama'}..."
        }
        
        presentation_data = await llm_analyzer.analyze_content(
            content=content,
            tone=tone,
            slide_count=slide_count,
            include_images=include_images
        )
        
        tasks[task_id] = {
            "status": "analyzed",
            "progress": 60,
            "message": "Структура презентации создана"
        }
        
        # Шаг 3: Генерация изображений (если нужно)
        if include_images:
            tasks[task_id] = {
                "status": "generating-images",
                "progress": 70,
                "message": "Генерация иллюстраций..."
            }
            await asyncio.sleep(1)  # Placeholder для реальной генерации
        
        # Шаг 4: Создание PPTX
        tasks[task_id] = {
            "status": "building",
            "progress": 85,
            "message": "Сборка презентации..."
        }
        
        output_dir = "/tmp/output"
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"presentation_{task_id}.pptx")
        
        builder = RostelecomPPTXBuilder()
        
        await asyncio.to_thread(
            builder.build_presentation,
            presentation_data,
            output_path
        )
        
        # Завершено
        tasks[task_id] = {
            "status": "complete",
            "progress": 100,
            "message": "Презентация готова!",
            "file_path": output_path,
            "data": presentation_data,
            "llm_provider": "QWEN API" if llm_analyzer.qwen_available else "Ollama"
        }
        
    except Exception as e:
        tasks[task_id] = {
            "status": "error",
            "progress": 0,
            "error": str(e),
            "message": f"Ошибка: {str(e)}"
        }


@app.get("/api/status/{task_id}", response_model=StatusResponse)
async def get_status(task_id: str):
    """
    Получение статуса задачи генерации
    
    Args:
        task_id: ID задачи
    
    Returns:
        Текущий статус и прогресс
    """
    
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    task_data = tasks[task_id]
    
    return StatusResponse(
        task_id=task_id,
        status=task_data.get("status", "unknown"),
        progress=task_data.get("progress", 0),
        message=task_data.get("message"),
        data=task_data.get("data"),
        error=task_data.get("error")
    )


@app.get("/api/download/{task_id}")
async def download_presentation(task_id: str):
    """
    Скачивание готовой презентации
    
    Args:
        task_id: ID задачи
    
    Returns:
        PPTX файл
    """
    
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    task = tasks[task_id]
    
    if task["status"] != "complete":
        raise HTTPException(
            status_code=400,
            detail=f"Презентация еще не готова. Статус: {task['status']}"
        )
    
    file_path = task.get("file_path")
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл презентации не найден")
    
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"presentation_rostelecom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
    )


@app.delete("/api/task/{task_id}")
async def delete_task(task_id: str):
    """
    Удаление задачи и очистка ресурсов
    
    Args:
        task_id: ID задачи
    """
    
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    task = tasks[task_id]
    
    # Удаление файла презентации
    if "file_path" in task and os.path.exists(task["file_path"]):
        os.remove(task["file_path"])
    
    # Удаление из памяти
    del tasks[task_id]
    
    return {"message": "Задача удалена", "task_id": task_id}


# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    print("\n" + "="*60)
    print("🚀 AI Генератор Презентаций Ростелеком")
    print("="*60)
    print(f"📡 Сервер: http://localhost:{port}")
    print(f"📚 Документация: http://localhost:{port}/docs")
    print(f"🤖 LLM: {'QWEN API ✅' if llm_analyzer.qwen_available else 'Ollama (fallback) ⚠️'}")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
