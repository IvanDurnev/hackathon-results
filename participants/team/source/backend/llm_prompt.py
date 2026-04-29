from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from llm_request import handle_file_upload

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate")
async def generate_presentation(
    prompt: str = Form(""),
    file: UploadFile = None,
    slides: int = Form(5),
    style: str = Form("corporate"),
    tone: str = Form("formal"),
    image_service: str = Form("sd"),
):
    """
    Основной endpoint генерации презентации.
    Поддерживает: только промпт | только файл | промпт + файл
    """
    if file:
        # Обработка загруженного файла
        return await handle_file_upload(
            file=file,
            prompt=prompt,
            slides=slides,
            style=style,
            tone=tone,
            image_service=image_service,
        )
    elif prompt:
        # Только текстовый промпт (без файла)
        from llm_request import summarize_to_structure
        result_slides = await summarize_to_structure(
            raw_text=prompt,
            user_prompt="",
            max_slides=slides,
            tone=tone,
        )
        return {"slides": result_slides, "image_service": image_service}
    else:
        raise HTTPException(status_code=400, detail="Требуется промпт или файл")