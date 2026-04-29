from docx import Document
from PyPDF2 import PdfReader
from fastapi import UploadFile
import os
import tempfile


async def extract_text_from_file(file: UploadFile) -> str:
    """
    Извлекает текст из загруженного файла (PDF или DOCX)
    """
    # Читаем содержимое файла
    content = await file.read()
    filename = file.filename.lower()

    # Создаем временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        tmp.write(content)
        temp_path = tmp.name

    text = ""

    try:
        if filename.endswith(".docx"):
            # Обработка DOCX
            doc = Document(temp_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    text += para.text + "\n"

        elif filename.endswith(".pdf"):
            # Обработка PDF
            reader = PdfReader(temp_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {filename}")

    except Exception as e:
        print(f"Ошибка при извлечении текста: {e}")
        text = f"[Ошибка чтения файла: {str(e)}]"

    finally:
        # Удаляем временный файл
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return text.strip()