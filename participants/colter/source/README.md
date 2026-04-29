# Редактор презентаций

MVP веб-приложения по техническому заданию из `ТЗ.md`. Архитектура:

- **Backend** — Python 3.11+, FastAPI, Pydantic 2, python-pptx. Файловое хранилище.
- **Frontend** — Vue 3 (Options API), Vite, Pinia, Vue Router, PrimeVue. Кастомный canvas редактора с координатами в EMU.
- **Контракт** — единая JSON-модель `TemplateDocument` / `PresentationDocument`, описанная в `ТЗ.md`.

# Запуск

Скопировать содержимое `.env.example` в `.env` и отредактировать, добавив токен. Запустить `docker compose up --build` для сборки и запуска контейнеров.
Приложение будет доступно по адресу `http://localhost:5173`.