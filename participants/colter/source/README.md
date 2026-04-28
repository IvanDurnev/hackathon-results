# amur-code — редактор презентаций

MVP веб-приложения по техническому заданию из `ТЗ.md`. Архитектура:

- **Backend** — Python 3.11+, FastAPI, Pydantic 2, python-pptx. Файловое хранилище.
- **Frontend** — Vue 3 (Options API), Vite, Pinia, Vue Router, PrimeVue. Кастомный canvas редактора с координатами в EMU.
- **Контракт** — единая JSON-модель `TemplateDocument` / `PresentationDocument`, описанная в `ТЗ.md`.

## Запуск

### Бэкенд

```bash
cd backend
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

При первом запуске в `backend/storage/` сидится дефолтный шаблон `template_business_01` (5 макетов: title/text/bullets/image/conclusion) и стартовая презентация.

API:

| Метод | Путь                                              | Описание                       |
| ----- | ------------------------------------------------- | ------------------------------ |
| GET   | `/api/templates`                                  | Список шаблонов                |
| GET   | `/api/templates/{id}`                             | Один шаблон                    |
| POST  | `/api/templates`                                  | Создать шаблон                 |
| PUT   | `/api/templates/{id}`                             | Сохранить шаблон               |
| GET   | `/api/presentations`                              | Список презентаций             |
| GET   | `/api/presentations/{id}`                         | Одна презентация               |
| POST  | `/api/presentations`                              | Создать презентацию            |
| PUT   | `/api/presentations/{id}`                         | Сохранить презентацию          |
| DELETE| `/api/presentations/{id}`                         | Удалить презентацию            |
| POST  | `/api/assets`                                     | Загрузить изображение          |
| POST  | `/api/presentations/{id}/export/pptx`             | Экспорт в PPTX (python-pptx)   |

### Фронтенд

```bash
cd frontend
npm install
npm run dev
```

Откройте http://localhost:5173. Vite проксирует `/api` и `/assets` на бэкенд (`:8000`).

## Что умеет редактор

- Презентации и шаблоны открываются в одном редакторе (режимы `presentation` / `template`).
- Слайды/макеты: добавить из выбранного макета, дублировать, удалить, drag-reorder в навигаторе.
- Элементы: текст, изображение, фигура (rect/roundRect/ellipse/triangle), линия. Перетаскивание, ресайз (8 ручек), удаление, выравнивание стрелками клавиатуры (Shift = крупный шаг).
- Текст редактируется двойным кликом (contenteditable). Стиль — шрифт, кегль, толщина, italic/underline, цвет, выравнивание, line-height.
- Inspector: координаты в EMU, размер, поворот, z-index, видимость, блокировка, role и `contentBehavior` (static/placeholder/generated/manual + readonly).
- Ограничения: maxChars, maxLines, overflow (clip/shrink/ellipsis/error). Inline-предупреждение на холсте.
- Фон слайда: цвет, изображение (через ассет), градиент.
- Asset Manager: загрузка PNG/JPG в `/api/assets`, использование в image-элементах и фоне.
- Undo/Redo (Ctrl/Cmd+Z, Cmd+Shift+Z) — командная история со снимками.
- Авто-сохранение по дебаунсу 2 с, вручную — кнопкой «Сохранить».
- Snap to grid (0.1 inch), zoom (Fit / + / -).
- Экспорт в PPTX — редактируемый текст, изображения, фигуры, линии, заметки.

## Структура

```
backend/
  app/
    models.py          # Pydantic-схемы из ТЗ
    storage.py         # файловое хранилище templates/presentations/assets
    validation.py      # кросс-полевые проверки
    pptx_export.py     # python-pptx экспортер
    seed.py            # дефолтный шаблон + стартовая презентация
    main.py            # FastAPI приложение
    routers/{templates,presentations,assets}.py
  storage/             # JSON-документы и загруженные ассеты
frontend/
  src/
    core/              # presentation-core (типы, factories, commands, EMU)
    stores/            # Pinia: document (с undo/redo), editor (UI state)
    components/
      editor/          # Canvas, ElementFrame, ElementRenderer, элементы
      navigator/       # SlideNavigator + SlideThumbnail
      inspector/       # Document/Slide/Element inspectors
      toolbar/         # EditorToolbar
    views/             # HomeView, PresentationEditor, TemplateEditor
    router/index.js
    api/client.js
```

## Что не вошло в MVP (по ТЗ)

LLM-генерация, импорт docx/pdf, генерация изображений, автоматическое оглавление, автосборка по промпту, rich text внутри одного блока, анимации, видео, диаграммы, полноценные таблицы, совместное редактирование. Архитектура (`contentBehavior.kind: "placeholder"`, `ImageGenerationMeta`, `ElementConstraints.splitStrategy`, `assets` как отдельная сущность) уже учитывает эти модули — их можно подключить без переписывания редактора.
