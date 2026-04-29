from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse

from file_parser import extract_text_from_file
from llm_service import generate_presentation_content
from ppt_generator import create_pptx

app = FastAPI()
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API is running"
    }



@app.post("/generate-presentation")
async def generate_presentation(
    prompt: str = Form(...),
    slides_count: int = Form(...),
    style: str = Form(...),
    tone: str = Form(...),
    file: UploadFile = File(...)
):
    # 1. Извлекаем текст из документа
    document_text = await extract_text_from_file(file)

    # 2. Генерация структуры презентации через LLM
    slides_data = generate_presentation_content(
        prompt=prompt,
        document_text=document_text,
        slides_count=slides_count,
        style=style,
        tone=tone
    )

    # 3. Создаем PPTX
    output_path = create_pptx(slides_data)

    # 4. Отдаем файл пользователю
    return FileResponse(
        path=output_path,
        filename="generated_presentation.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
