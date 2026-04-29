import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pypdf
from docx import Document
from dotenv import load_dotenv
import uuid
import re
from app.services.llm_service import generate_structure
from app.services.image_service import generate_image
from app.services.pptx_generator import generate_presentation

load_dotenv()

app = FastAPI(title="AI PPTX Generator")
os.makedirs("uploads", exist_ok=True)

# CORS - разрешаем запросы с React (только localhost в разработке)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем папку uploads как статическую (для доступа к картинкам)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Шаблонизатор (если нужен старый HTML)
# templates = Jinja2Templates(directory="templates")

# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    """Проверка здоровья сервера"""
    return JSONResponse({"status": "ok"})

def sanitize_filename(filename: str) -> str:
    """Очистка имени файла от опасных символов"""
    # Удаляем все символы кроме букв, цифр, точки, дефиса, подчеркивания
    sanitized = re.sub(r'[^\w.\-]', '_', filename)
    # Ограничиваем длину
    return sanitized[:100]

def extract_text(file: UploadFile, session_id: str) -> str:
    """Извлечение текста из PDF/DOCX"""
    if file is None or file.filename == "":
        return ""

    session_dir = os.path.join("uploads", session_id)
    os.makedirs(session_dir, exist_ok=True)

    safe_filename = sanitize_filename(file.filename)
    path = os.path.join(session_dir, safe_filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = ""
    try:
        if file.filename.lower().endswith(".pdf"):
            with open(path, "rb") as f:
                reader = pypdf.PdfReader(f)
                text = "\n".join([p.extract_text() or "" for p in reader.pages])
        elif file.filename.lower().endswith(".docx"):
            doc = Document(path)
            text = "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

    return text[:3000]

@app.post("/api/generate")
async def generate(
    prompt: str = Form(...),
    num_slides: int = Form(10),
    style: str = Form("corporate"),
    tone: str = Form("professional"),
    include_images: str = Form("true"),
    template_id: int = Form(1),
    file: UploadFile = File(None, alias="document")
):
    """Генерация презентации"""

    # Валидация входных параметров
    if not prompt or len(prompt.strip()) < 3:
        return JSONResponse({"error": "Промпт должен быть минимум 3 символа"}, status_code=400)

    num_slides = max(1, min(20, int(num_slides)))  # 1-20 слайдов
    template_id = max(1, min(3, int(template_id)))  # 1-3 шаблона
    include_images_bool = include_images.lower() == "true"

    # Создаём уникальный ID сессии
    session_id = str(uuid.uuid4())
    session_dir = os.path.join("uploads", session_id)
    os.makedirs(session_dir, exist_ok=True)

    try:
        doc_text = ""
        if file and file.filename:
            doc_text = extract_text(file, session_id)

        # Генерируем структуру слайдов
        try:
            structure = generate_structure(prompt, doc_text, num_slides, style, tone)
        except Exception as e:
            print(f"Error in generate: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

        if structure is None:
            return JSONResponse({"error": "Ошибка генерации структуры слайдов"}, status_code=500)

        # Генерируем изображения для каждого слайда (если включено)
        if include_images_bool:
            for i, slide in enumerate(structure):
                if slide.get("image_prompt"):
                    image_path = os.path.join(session_dir, f"img_{i}.png")
                    generate_image(slide["image_prompt"], image_path)

        # Создаем PPTX в директории сессии с выбранным шаблоном
        pptx_path = os.path.join(session_dir, "result.pptx")
        generate_presentation(structure, pptx_path, style_name=style, template_id=template_id)

        return JSONResponse({"slides": structure, "message": "Готово!", "sessionId": session_id})

    except Exception as e:
        print(f"Error in generate: {e}")
        import traceback
        traceback.print_exc()
        # Очищаем директорию сессии при ошибке
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...), slide_index: int = Form(...), session_id: str = Form(...)):
    """Загрузка пользовательского изображения для слайда"""
    try:
        session_dir = os.path.join("uploads", session_id)
        os.makedirs(session_dir, exist_ok=True)

        # Сохраняем файл
        safe_filename = sanitize_filename(file.filename)
        file_path = os.path.join(session_dir, f"slide_{slide_index}_{safe_filename}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"✅ Изображение загружено: {file_path}")

        return JSONResponse({
            "message": "Изображение загружено",
            "file_path": file_path
        })
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/regenerate-image")
async def regenerate_image(prompt: str = Form(...), slide_index: int = Form(...), session_id: str = Form(...)):
    """Перегенерация изображения через AI"""
    try:
        session_dir = os.path.join("uploads", session_id)
        os.makedirs(session_dir, exist_ok=True)

        file_path = os.path.join(session_dir, f"img_{slide_index}.png")

        # Генерируем новое изображение
        result = generate_image(prompt, file_path)

        if result:
            print(f"✅ Изображение перегенерировано: {file_path}")
            return JSONResponse({
                "message": "Изображение сгенерировано",
                "file_path": file_path
            })
        else:
            return JSONResponse({"error": "Не удалось сгенерировать"}, status_code=500)

    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/download/{session_id}")
async def download(session_id: str):
    """Скачивание готовой презентации"""
    pptx_path = os.path.join("uploads", session_id, "result.pptx")
    if not os.path.exists(pptx_path):
        return JSONResponse({"error": "Файл ещё не сгенерирован"}, status_code=404)

    return FileResponse(
        pptx_path,
        media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        filename='presentation.pptx'
    )
