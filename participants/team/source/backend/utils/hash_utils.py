import hashlib

def hash_prompt(prompt: str) -> str:
    """
    64‑символьный SHA‑256 хеш.
    Используется как имя файла в кеш‑директории.
    """
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()
