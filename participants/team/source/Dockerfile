FROM node:22-bookworm-slim AS frontend-build

WORKDIR /build/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


FROM python:3.12-slim AS runtime

ENV APP_ENV=production \
    AI_MODULE_ENABLED=1 \
    AI_MODULE_HOST=127.0.0.1 \
    AI_MODULE_PORT=8091 \
    AI_MODULE_URL=http://127.0.0.1:8091/api/ai \
    DATA_DIR=/data \
    DISABLE_SQLITE=1 \
    FLASK_APP=wsgi \
    FRONTEND_DIST_DIR=/app/frontend/dist \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/backend:/app/AImodule \
    PYTHONUNBUFFERED=1 \
    STT_LANGUAGE=ru \
    STT_MODEL=@cf/openai/whisper-large-v3-turbo \
    STT_PROVIDER=cloudflare \
    UPLOAD_FOLDER=/data/uploads

WORKDIR /app

COPY backend/requirements.txt /tmp/requirements.txt
COPY AImodule/requirements.txt /tmp/ai-requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt -r /tmp/ai-requirements.txt

COPY backend ./backend
COPY AImodule ./AImodule
COPY --from=frontend-build /build/frontend/dist ./frontend/dist
COPY deploy/amvera-entrypoint.sh /app/deploy/amvera-entrypoint.sh

RUN chmod +x /app/deploy/amvera-entrypoint.sh \
    && mkdir -p /data/uploads

EXPOSE 8080

ENTRYPOINT ["/app/deploy/amvera-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]
