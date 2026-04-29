"""
Модуль для извлечения текста из PDF и DOCX файлов.
Используется для анализа загруженных документов.
"""

import os
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """
    Извлекает текст из PDF файла.
    
    Args:
        file_path: Путь к PDF файлу
        
    Returns:
        Текст из всех страниц, разделённый переносами строк
    """
    try:
        reader = PdfReader(file_path)
        text_pages = []
        
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text.strip())
        
        return "\n\n".join(text_pages)
    
    except Exception as e:
        print(f"Ошибка при чтении PDF: {e}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """
    Извлекает текст из DOCX файла.
    
    Args:
        file_path: Путь к DOCX файлу
        
    Returns:
        Текст из всех параграфов документа
    """
    try:
        doc = Document(file_path)
        paragraphs = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())
        
        return "\n\n".join(paragraphs)
    
    except Exception as e:
        print(f"Ошибка при чтении DOCX: {e}")
        return ""


def parse_document(file_path: str) -> str:
    """
    Определяет тип файла и извлекает текст.
    
    Args:
        file_path: Путь к файлу (PDF или DOCX)
        
    Returns:
        Извлечённый текст
        
    Raises:
        ValueError: Если формат файла не поддерживается
    """
    # Получаем расширение файла
    ext = os.path.splitext(file_path)[1].lower()
    
    print(f"📄 Парсинг файла: {file_path} (расширение: {ext})")
    
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
        print(f"✅ Из PDF извлечено символов: {len(text)}")
        return text
    
    elif ext in (".docx", ".doc"):
        text = extract_text_from_docx(file_path)
        print(f"✅ Из DOCX извлечено символов: {len(text)}")
        return text
    
    else:
        error_msg = f"Неподдерживаемый формат файла: {ext}. Разрешены: .pdf, .docx"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)


def truncate_text(text: str, max_length: int = 3000) -> str:
    """
    Обрезает текст до максимальной длины.
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина в символах
        
    Returns:
        Обрезанный текст
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "... [текст обрезан]"