FROM node:22-bookworm-slim AS frontend-build

WORKDIR /build/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


FROM python:3.12-slim AS runtime

ENV APP_ENV=production \
    DATA_DIR=/data \
    FLASK_APP=wsgi \
    FRONTEND_DIST_DIR=/app/frontend/dist \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/backend \
    PYTHONUNBUFFERED=1 \
    UPLOAD_FOLDER=/data/uploads

WORKDIR /app

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend ./backend
COPY --from=frontend-build /build/frontend/dist ./frontend/dist
COPY deploy/amvera-entrypoint.sh /app/deploy/amvera-entrypoint.sh

RUN chmod +x /app/deploy/amvera-entrypoint.sh \
    && mkdir -p /data/uploads

EXPOSE 8080

ENTRYPOINT ["/app/deploy/amvera-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]
