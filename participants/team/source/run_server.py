import sys
import os
from pathlib import Path

# Добавляем backend в путь
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Импортируем приложение
from app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
