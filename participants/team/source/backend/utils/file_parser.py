import io
from pathlib import Path

import docx
import PyPDF2


def _read_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def _read_docx(data: bytes) -> str:
    document = docx.Document(io.BytesIO(data))
    return "\n".join(p.text for p in document.paragraphs)


def _read_pdf(data: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(data))
    text = ""
    for page in reader.pages:
        txt = page.extract_text()
        if txt:
            text += txt + "\n"
    return text


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Поддерживаемые форматы: .txt, .docx, .pdf.
    Возвращает «чистый» текст.
    """
    ext = Path(filename).suffix.lower()
    if ext == ".txt":
        return _read_txt(file_bytes)
    if ext == ".docx":
        return _read_docx(file_bytes)
    if ext == ".pdf":
        return _read_pdf(file_bytes)

    raise ValueError(f"Unsupported file type: {ext}")
