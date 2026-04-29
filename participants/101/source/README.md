# 🎨 AI PPTX Generator  

**Автоматическая генерация интеллектуальных презентаций на базе ИИ**

Проект для хакатона "Амурский код" - приложение, которое генерирует профессиональные PPTX презентации на основе текстовых описаний, используя искусственный интеллект.

## 🌟 Основные возможности

### 🤖 ИИ-управляемый контент
- Автоматическая генерация содержания слайдов на основе промпта
- Поддержка 3 тонов повествления: профессиональный, дружелюбный, академический
- Анализ документов (PDF, DOCX) для составления презентаций

### 🎨 Гибкий дизайн
- **3 встроенных стиля оформления**: Корпоративный, Креативный, Минималистичный
- **3 шаблона разметки слайдов**:
  - Двухколончная (текст + изображение)
  - Полноширинная (текст на всю ширину)
  - Сетчатая разметка (множественные блоки)

### 🖼️ Визуальное содержание
- Автоматическая генерация изображений для слайдов (Yandex ART)

### ✏️ Интерактивный редактор
- **Редактирование текста в реальном времени**
- **Режим перемещения элементов** - перетаскивание заголовков, текста и изображений
- Предпросмотр слайдов
- Навигация между слайдами

### 💾 Сохранение и экспорт
- Экспорт в PPTX (PowerPoint) формате
- Сохранение промпта в localStorage (они не теряются при ошибке)


## 🏗️ Архитектура

```
┌─────────────────────────────────────────┐
│        Frontend (React + Vite)          │
│    - Генерация формы с параметрами      │
│    - Редактор слайдов                   │
│                                         │
└──────────┬──────────────────────────────┘
           │ HTTP/REST API
┌──────────▼──────────────────────────────┐
│      Backend (FastAPI + Python)         │
│    - Анализ текста (LLM)                │
│    - Генерация структуры слайдов        │
│    - Создание PPTX файлов               │
│    - Генерация изображений              │
└──────────┬──────────────────────────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼───┐    ┌────▼────┐
│ LLM   │    │Image Gen │
│Service│    │ Service  │
└───────┘    └──────────┘
```

## 📋 Требования
- Python 3.14 (для локальной разработки)
- Node.js 24.15 LTS (для локальной разработки)
- 2GB свободной памяти (минимум)

## 🚀 Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone <repository>
cd "<директория, куда был склонирован репозиторий>"
```
### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Сервер будет доступен на `http://localhost:8000`

3. ### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Приложение будет доступно на `http://localhost:3000`

**API документация**: http://localhost:8000/docs

## 📁 Структура проекта

```
.
├── backend/                    # Python FastAPI приложение
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Основное приложение FastAPI
│   │   ├── config.py          # Конфигурация
│   │   ├── models.py          # Pydantic модели
│   │   ├── services/          # Бизнес-логика
│   │   │   ├── llm_service.py        # Генерация контента при помощи LLM
│   │   │   ├── image_service.py      # Генерация изображений через LLM
│   │   │   └── pptx_generator.py     # Создание PPTX (3 шаблона)
│   │   └── utils/
│   │       └── logger.py      # Логирование
│   ├── requirements.txt        # Python зависимости
│   └── .env.example          # Пример переменных окружения
│
├── frontend/                   # React приложение
│   ├── src/
│   │   ├── App.jsx           # Основной компонент (с обработкой ошибок)
│   │   ├── main.jsx          # Entry point
│   │   ├── components/
│   │   │   ├── GenerationForm.jsx      # Форма с сохранением настроек
│   │   │   ├── SlidesPreview.jsx       # Предпросмотр слайдов
│   │   │   └── SlideEditor.jsx         # Редактор 
│   │   ├── services/
│   │   │   └── api.js        # API сервис
│   │   └── styles/
│   ├── package.json          # NPM зависимости
│   └── .env.example         # Пример переменных окружения
│
└── README.md                # Этот файл
```

## 🔧 API Endpoints

### Генерация презентации

```
POST /api/generate
Content-Type: multipart/form-data

Parameters:
  - prompt (string, required): Тема презентации
  - num_slides (int, optional): Количество слайдов (1-20)
  - style (string, optional): Стиль (corporate, creative, minimalist)
  - tone (string, optional): Тон (professional, friendly, academic)
  - template_id (int, optional): Шаблон разметки (1-3)
  - include_images (boolean, optional): Генерировать изображения
  - document (file, optional): PDF или DOCX документ

Response:
{
  "slides": [...],
  "sessionId": "uuid",
  "message": "Готово!"
}
```

### Скачивание PPTX

```
GET /api/download/{sessionId}

Response: Binary PPTX file
```

### Проверка здоровья

```
GET /health

Response:
{
  "status": "ok"
}
```

Полная документация API доступна на `/docs` (Swagger UI)


## 🐛 Решение проблем

### Ошибка подключения API

Убедитесь, что backend работает:
```bash
curl http://localhost:8000/health
```


Разработано для хакатона "Амурский код"

---

