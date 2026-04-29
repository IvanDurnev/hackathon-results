import os
import sys
import uuid
import shutil
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 🔧 АВТО-ОПРЕДЕЛЕНИЕ ПАПКИ (работает и в VS Code, и в готовом .exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # Папка, где лежит .exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Папка проекта в VS Code

# Загружаем .env строго из папки рядом с программой
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Добавляем корневую папку в пути поиска Python (чтобы работали импорты)
sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from parsers.document_parser import parse_document, truncate_text
from ai.llm_service import generate_slide_structure
from ai.image_service import generate_image
from pptx_builder import build_pptx

app = FastAPI(title="AI Генератор Презентаций")

# Пути к папкам теперь привязаны к BASE_DIR
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory="templates")

TMP_DIR = os.path.join(BASE_DIR, "tmp")
os.makedirs(TMP_DIR, exist_ok=True)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"✅ Сервер запущен. Рабочая папка: {BASE_DIR}")

app = FastAPI(
    title="AI Генератор Презентаций",
    description="Сервис для автоматической генерации PPTX через API Ростелеком",
    version="1.0.0"
)

# Монтируем статические файлы (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настраиваем шаблоны Jinja2
templates = Jinja2Templates(directory="templates")

# Папка для временных файлов
TMP_DIR = Path("tmp")
TMP_DIR.mkdir(exist_ok=True)

print("✅ Сервер инициализирован")


# ============================================
# Главная страница
# ============================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    
    return templates.TemplateResponse(request=request, name="index.html")


# ============================================
# API: Генерация презентации
# ============================================

@app.post("/generate")
async def generate_presentation(
    request: Request,    # <--- ВОТ ЭТУ СТРОКУ НУЖНО ДОБАВИТЬ
    user_prompt: str = Form(...),
    slides_count: int = Form(5),
    style: str = Form("corporate"),
    tone: str = Form("professional"),
    file: UploadFile = File(None)
):
    """
    Генерирует презентацию на основе запроса и файла.
    
    Args:
        user_prompt: Текстовый запрос пользователя
        slides_count: Количество слайдов (1-20)
        style: Стиль презентации
        tone: Тон изложения
        file: Загруженный файл (PDF/DOCX)
        
    Returns:
        JSON с job_id и ссылками на скачивание
    """
    
    print(f"\n{'='*60}")
    print(f"🚀 НОВАЯ ЗАЯВКА НА ГЕНЕРАЦИЮ")
    print(f"{'='*60}")
    print(f"📝 Запрос: {user_prompt[:100]}...")
    print(f"📊 Слайдов: {slides_count}")
    print(f"🎨 Стиль: {style}, Тон: {tone}")
    
    # Валидация количества слайдов
    if slides_count < 1:
        slides_count = 1
    elif slides_count > 20:
        slides_count = 20
    
    # Создаём уникальную папку для задачи
    clean_prompt = "".join(x for x in user_prompt[:20] if x.isalnum() or x in "._- ")
    job_id = f"{clean_prompt}_{str(uuid.uuid4())[:8]}"
    job_dir = Path(OUTPUT_DIR) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Результаты будут сохранены в: {job_dir}")
    
    # ============================================
    # Шаг 1: Обработка загруженного файла
    # ============================================
    
    doc_text = ""
    
    if file and file.filename:
        print(f"📎 Получен файл: {file.filename}")
        
        # Проверяем расширение
        if not file.filename.lower().endswith((".pdf", ".docx", ".doc")):
            raise HTTPException(
                status_code=400,
                detail="Поддерживаются только файлы PDF и DOCX"
            )
        
        # Сохраняем файл
        file_path = job_dir / file.filename
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            print(f"✅ Файл сохранён: {file_path}")
        except Exception as e:
            print(f"❌ Ошибка сохранения файла: {e}")
            raise HTTPException(status_code=500, detail="Ошибка загрузки файла")
        
        # Извлекаем текст
        try:
            doc_text = parse_document(str(file_path))
            doc_text = truncate_text(doc_text, max_length=3000)
            print(f"✅ Текст извлечён ({len(doc_text)} символов)")
        except Exception as e:
            print(f"⚠️  Не удалось извлечь текст: {e}")
            doc_text = ""
    else:
        print("📎 Файл не загружен")
    
    # ============================================
    # Шаг 2: Генерация структуры слайдов (LLM)
    # ============================================
    
    print("\n🤖 Шаг 2: Генерация структуры слайдов...")
    
    slides_json = generate_slide_structure(
        user_prompt=user_prompt,
        doc_text=doc_text,
        num_slides=slides_count,
        style=style,
        tone=tone
    )
    
    if not slides_json or not slides_json.get("slides"):
        print("❌ Ошибка: LLM вернула пустую структуру")
        raise HTTPException(status_code=500, detail="Ошибка генерации структуры")
    
    with open(job_dir / "structure.json", "w", encoding="utf-8") as f:
        json.dump(slides_json, f, ensure_ascii=False, indent=4)
    actual_slides = len(slides_json["slides"])
    print(f"✅ Сгенерировано слайдов: {actual_slides}")
    
   # ============================================
    # Шаг 3: Генерация изображений
    # ============================================
    
    print("\n🎨 Шаг 3: Генерация изображений...")
    
    image_dir = job_dir / "images"
    image_dir.mkdir(exist_ok=True)
    
    for i, slide in enumerate(slides_json.get("slides", [])):
        img_prompt = slide.get("image_prompt", "").strip()
        
        if img_prompt:
            # Локальное имя файла
            img_filename = f"slide_{i}.png"
            # Полный путь для сохранения файла на диск
            full_save_path = str(image_dir / img_filename)
            
            # Вызываем генерацию
            result_path = generate_image(
                prompt=img_prompt,
                save_path=full_save_path,
                aspect="16:9"
            )
            
            if result_path:
                # ВАЖНО: сохраняем в структуру слайда только имя файла!
                # Сборщик презентации сам добавит нужную папку.
                slide["image_path"] = img_filename 
                print(f"   ✅ Слайд {i+1}: изображение сгенерировано")
            else:
                slide["image_path"] = None
                print(f"   ⚠️  Слайд {i+1}: изображение не сгенерировано")
        else:
            slide["image_path"] = None
            print(f"   ⏭  Слайд {i+1}: нет prompt'а для картинки")
    
    # ============================================
    # Шаг 4: Сборка PPTX
    # ============================================
    
    print("\n📊 Шаг 4: Сборка презентации...")
    
    pptx_path = str(job_dir / "presentation.pptx")
    
    try:
        build_pptx(
            slides_data=slides_json,
            output_path=pptx_path,
            image_dir=str(image_dir)
        )
        print(f"✅ Презентация собрана: {pptx_path}")
    except Exception as e:
        print(f"❌ Ошибка сборки PPTX: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания презентации")
    
    # ============================================
    # Возвращаем результат
    # ============================================
    
    print(f"\n{'='*60}")
    print(f"✅ ГЕНЕРАЦИЯ ЗАВЕРШЕНА")
    print(f"{'='*60}\n")
    
   # В самом конце функции generate_presentation верни этот блок:
    return templates.TemplateResponse(
        request=request, 
        name="preview.html", 
        context={
            "download_url": f"/download/{job_id}",
            "slides_count": actual_slides
        }
    )

# ============================================
# Страница предпросмотра
# ============================================

@app.get("/preview/{job_id}", response_class=HTMLResponse)
async def preview_presentation(request: Request, job_id: str):
    """
    Страница предпросмотра презентации.
    """
    pptx_path = TMP_DIR / job_id / "presentation.pptx"
    
    if not pptx_path.exists():
        raise HTTPException(status_code=404, detail="Презентация не найдена")
    
    return templates.TemplateResponse(
        "preview.html",
        {"request": request, "job_id": job_id}
    )


# ============================================
# Скачивание презентации
# ============================================

@app.get("/download/{job_id}")
async def download_presentation(job_id: str):
    # ВАЖНО: Ищем теперь в OUTPUT_DIR, а не в TMP_DIR
    pptx_path = Path(OUTPUT_DIR) / job_id / "presentation.pptx"
    
    print(f"🔍 Ищу файл по пути: {pptx_path}") # Это поможет тебе увидеть в консоли, куда именно стучится сервер
    
    if not pptx_path.exists():
        print(f"❌ Файл не найден!")
        raise HTTPException(status_code=404, detail="Презентация не найдена")
    
    return FileResponse(
        path=pptx_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename="presentation.pptx"
    )


# ============================================
# Health check
# ============================================

@app.get("/health")
async def health_check():
    """
    Проверка работоспособности API.
    """
    return {
        "status": "ok",
        "service": "AI PPTX Generator",
        "version": "1.0.0"
    }


# ============================================
# Запуск сервера
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 ЗАПУСК СЕРВЕРА AI PPTX GENERATOR")
    print("="*60)
    print("\nОткройте в браузере: http://127.0.0.1:8000")
    print("\nНажмите Ctrl+C для остановки\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)