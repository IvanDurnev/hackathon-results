from docx import Document
from PyPDF2 import PdfReader
from fastapi import UploadFile
import os


async def extract_text_from_file(file: UploadFile):
    content = await file.read()
    filename = file.filename.lower()

    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(content)

    text = ""

    if filename.endswith(".docx"):
        doc = Document(temp_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    elif filename.endswith(".pdf"):
        reader = PdfReader(temp_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    os.remove(temp_path)

    return text