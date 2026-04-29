from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import traceback

from file_parser import extract_text_from_file
from llm_service import generate_presentation_content
from ppt_generator import create_pptx

app = FastAPI(
    title="AI Presentation Generator API",
    description="API для автоматической генерации презентаций на основе ИИ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Пути
BACKEND_DIR = Path(__file__).parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"

# Создаём папки
os.makedirs("generated", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

print(f"📁 Backend:  {BACKEND_DIR}")
print(f"📁 Frontend: {FRONTEND_DIR}")
print(f"📁 Frontend exists: {FRONTEND_DIR.exists()}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница"""
    html_path = FRONTEND_DIR / "index.html"

    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Presentation Generator</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                padding: 20px;
            }}
            .card {{
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 48px;
                text-align: center;
                max-width: 500px;
            }}
            h1 {{ font-size: 24px; margin-bottom: 16px; }}
            p {{ color: #94a3b8; margin-bottom: 24px; line-height: 1.6; }}
            .links {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }}
            a {{
                display: inline-block;
                padding: 12px 24px;
                background: #3b82f6;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 500;
                transition: background 0.2s;
            }}
            a:hover {{ background: #2563eb; }}
            a.secondary {{ background: rgba(255,255,255,0.1); }}
            a.secondary:hover {{ background: rgba(255,255,255,0.2); }}
            code {{
                background: rgba(255,255,255,0.1);
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 13px;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎯 AI Presentation Generator</h1>
            <p>Фронтенд не найден. Убедитесь, что папка <code>frontend</code> с файлом <code>index.html</code> находится рядом с <code>backend</code>.</p>
            <div class="links">
                <a href="/docs">📚 API Документация</a>
                <a href="/redoc" class="secondary">📖 ReDoc</a>
            </div>
        </div>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {
        "status": "ok",
        "service": "AI Presentation Generator",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/generate-presentation")
async def generate_presentation(
        prompt: str = Form(default=""),
        slides_count: int = Form(default=5, ge=1, le=20),
        style: str = Form(default="professional"),
        tone: str = Form(default="formal"),
        file: UploadFile = File(default=None)
):
    """
    Генерация презентации на основе текстового запроса и/или документа.

    - **prompt**: Тема презентации
    - **slides_count**: Количество слайдов (1-20)
    - **style**: Стиль оформления (professional, academic, minimal, business, creative)
    - **tone**: Тон текста (formal, informative, persuasive, friendly)
    - **file**: PDF или DOCX файл (опционально)
    """
    try:
        print(f"📥 Запрос: prompt='{prompt[:50]}...', slides={slides_count}, style={style}, tone={tone}")

        # Извлекаем текст из документа
        document_text = ""
        if file and file.filename:
            print(f"📄 Файл: {file.filename}")
            document_text = await extract_text_from_file(file)
            print(f"📝 Текст: {len(document_text)} символов")

        # Проверка
        if not prompt.strip() and not document_text.strip():
            raise HTTPException(status_code=400, detail="Укажите тему или загрузите документ")

        # Генерация контента
        print("🤖 LLM генерация...")
        slides_data = generate_presentation_content(
            prompt=prompt or "Презентация",
            document_text=document_text,
            slides_count=slides_count,
            style=style,
            tone=tone
        )
        print(f"✅ Слайдов: {len(slides_data)}")

        # Создание PPTX
        print("📊 Создание PPTX...")
        output_path = create_pptx(slides_data)
        print(f"💾 Сохранено: {output_path}")

        return FileResponse(
            path=output_path,
            filename="presentation.pptx",
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": "attachment; filename=presentation.pptx"}
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


# Раздача статики фронтенда (в самом конце)
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")