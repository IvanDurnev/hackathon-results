FROM python:3.12-slim

# Устанавливаем зависимости системные (для pdf, docx)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем только requirements и устанавливаем их (layer‑кеш)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Открываем порт, который будет слушать uvicorn
EXPOSE 8000

# Переменные окружения (можно переопределять в docker‑compose)
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
