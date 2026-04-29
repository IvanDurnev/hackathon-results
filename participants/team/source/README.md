<div align="center">

  <h1>Интеллектуальный отбор данных</h1>

  <p>
    <b>Конструктор аналитических выборок для бюджетного планирования Амурской области</b>
  </p>

  <img src="./image.jpg">
  <p>
    <sub>Команда «Некодеры»: Александр Самарин и Степан Исаков</sub>
  </p>

  <p style="margin-top: 10px;">
    <a href="https://necoders.tech/">
      <img src="https://img.shields.io/badge/Демо-necoders.tech-2f6fed?style=for-the-badge" alt="Демо">
    </a>
    <img src="https://img.shields.io/badge/Команда-Некодеры-8ade3f?style=for-the-badge" alt="Команда Некодеры">
    <img src="https://img.shields.io/badge/Frontend-React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
    <img src="https://img.shields.io/badge/Backend-Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Deploy-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  </p>

  <p>
    <img src="https://img.shields.io/badge/Product-UI%2FUX-7c3aed?style=flat-square" alt="Product UI/UX">
    <img src="https://img.shields.io/badge/Architecture-Fullstack-0f766e?style=flat-square" alt="Architecture Fullstack">
    <img src="https://img.shields.io/badge/Data-ETL%20%2B%20Analytics-2563eb?style=flat-square" alt="ETL Analytics">
    <img src="https://img.shields.io/badge/Delivery-Docker%20%2B%20Amvera-ea580c?style=flat-square" alt="Docker Amvera">
  </p>

  <p>
    <a href="https://necoders.tech/">Открыть демо</a>
    ·
    <a href="https://disk.yandex.ru/i/l3V9591GVSwTWA">Скринкаст</a>
    ·
    <a href="https://example.com/presentation">Презентация</a>
  </p>

</div>

---

## Ссылки

- **Развернутое решение:** [https://necoders.tech/](https://necoders.tech/)
- **Скринкаст:** [https://disk.yandex.ru/i/l3V9591GVSwTWA](https://disk.yandex.ru/i/l3V9591GVSwTWA)
- **Презентация:** [ссылка будет добавлена](https://example.com/presentation)

---

## О продукте

Проект решает кейс **«Интеллектуальный отбор данных. Конструктор аналитических выборок для бюджетного планирования»**. Платформа помогает специалистам собирать единую аналитическую картину по бюджетным объектам без ручного сведения CSV-выгрузок из разных ведомственных систем.

Система работает с обезличенными данными из набора кейса:

- **РЧБ** - бюджетные данные по месяцам нарастающим итогом: лимиты, обязательства, кассовые выплаты, остатки;
- **Соглашения** - межбюджетные трансферты, субсидии учреждениям и иным получателям;
- **ГЗ** - контракты, договоры, бюджетные строки и факты оплат;
- **БУАУ** - выплаты бюджетным и автономным учреждениям.

Вместо работы с тяжелыми таблицами пользователь выбирает объект, показатели и период, а приложение формирует итоговую таблицу, динамику, сравнение дат, расшифровку строк и экспорт.

---

## Ключевые возможности

- **Импорт источников администратором.** CSV-файлы проходят нормализацию кодировок, разделителей, дат, сумм и бюджетных кодов, после чего сохраняются в аналитическую базу.
- **Контрольные шаблоны.** Реализованы сценарии `КИК`, `СКК`, `Раздел 3. 2/3` и `ОКВ` по правилам контрольного Excel-примера.
- **Поиск объекта.** Можно искать по коду, названию, получателю, номеру договора или фрагменту бюджетной классификации.
- **Показатели по разным источникам.** Поддерживаются лимиты, бюджетные обязательства, касса, соглашения, договоры, оплаты и выплаты БУАУ.
- **Периоды и сравнение дат.** Для накопительных выгрузок РЧБ и БУАУ берется актуальный снимок на дату окончания периода, а для договоров и платежей используется событийная дата.
- **Качество данных.** Отдельная вкладка показывает предупреждения: платеж без договора, договор без бюджетной строки, распределение суммы между строками и ошибки парсинга.
- **Интерактивные результаты.** Таблица, итоговые суммы, помесячная динамика, расшифровка документов и история запусков в текущей сессии.
- **Экспорт.** Результат можно скачать в `CSV` или `XLSX`; в Excel добавляется лист с предупреждениями активной выборки.
- **Помощник и голосовой ввод.** В интерфейсе есть опциональный помощник для подбора параметров и объяснения выборок. Он вынесен в отдельный адаптер и может обращаться к совместимому внешнему зарубежному ресурсу; голосовой ввод реализован таким же изолированным способом через сервис распознавания речи. В закрытом контуре эти компоненты можно отключить или заменить внутренними аналогами без изменения ядра аналитики.

---

## Стек

### Frontend

- **React 19** + **TypeScript** - интерфейс конструктора, авторизации, профиля и админ-раздела.
- **Vite 6** - сборка и dev-сервер.
- **Tailwind CSS 4** + локальный UI-kit - адаптивная корпоративная верстка.
- **TanStack Query** - загрузка, кэширование и синхронизация API-данных.
- **React Router 7** - маршрутизация и защищенные страницы.
- **React Hook Form** + **Zod** - формы и валидация.
- **Radix UI**, **lucide-react**, **sonner** - доступные UI-примитивы, иконки и уведомления.

### Backend

- **Python 3.12**.
- **Flask 3** - REST API и раздача собранного frontend в production.
- **SQLAlchemy** + **Flask-Migrate/Alembic** - модели, миграции и работа с БД.
- **Pydantic 2** - API-схемы и валидация входных данных.
- **Flask-Login** - сессионная авторизация и роли `user` / `admin`.
- **openpyxl** - формирование Excel-экспорта.
- **Gunicorn** - production-запуск.

### Инфраструктура

- **Docker multi-stage build** - сборка frontend и запуск backend одним контейнером.
- **Amvera** - подготовленный `amvera.yaml`, постоянное хранилище `/data` и entrypoint с миграциями.
- **SQLite** - удобен для локального контура.
- **PostgreSQL** - рекомендован для production/Amvera.
- **Отдельный интеллектуальный адаптер** - изолированный Python-сервис, который подключается к backend только по внутреннему HTTP API.

---

## Архитектура приложения

```mermaid
flowchart LR
    A["Администратор"] --> B["Импорт CSV / папки task"]
    B --> C["Backend Flask API"]
    C --> D["Парсинг и нормализация"]
    D --> E["Аналитическая БД"]
    E --> F["Query engine"]
    F --> G["REST API /api/v1/analytics"]
    G --> H["React workspace"]
    H --> I["Таблицы, графики, экспорт"]
    H --> J["Опциональный помощник"]
    J --> K["Изолированный внешний/заменяемый сервис"]
```

Приложение построено как **модульный монолит**:

- `backend/app/api/v1` собирает API под префиксом `/api/v1`;
- `auth`, `users`, `admin`, `files` отвечают за базовую платформенную часть;
- `budget_constructor` содержит доменную аналитику: импорт, поиск, шаблоны, выборки, сравнение, динамику, расшифровку и экспорт;
- `assistant` проксирует запросы к отдельному помощнику и не смешивает внешние сервисы с ядром аналитики;
- `frontend/src` разделен на `app`, `pages`, `widgets`, `features`, `entities`, `shared`.

Основной поток данных:

1. Администратор импортирует набор CSV из источников кейса.
2. Backend определяет формат файлов, нормализует данные и сохраняет аналитические факты.
3. Пользователь выбирает шаблон или ищет объект вручную.
4. Query engine агрегирует показатели по объектам, источникам и периоду.
5. Frontend показывает таблицу, график, сравнение дат, предупреждения качества и экспорт.

---

## Структура репозитория

```text
newhaka_full/
├── backend/                  # Flask API, доменная логика, миграции, тесты
│   ├── app/
│   │   ├── api/v1/           # Регистрация API endpoints
│   │   ├── core/             # Ошибки, ответы, безопасность, пагинация
│   │   └── modules/
│   │       ├── auth/         # Регистрация, вход, сессии
│   │       ├── users/        # Профиль пользователя
│   │       ├── admin/        # Управление аккаунтами
│   │       ├── files/        # Файловое хранилище
│   │       ├── assistant/    # Прокси к помощнику
│   │       └── budget_constructor/
│   │           ├── engine.py     # Агрегация, шаблоны, поиск, динамика
│   │           ├── parsing.py    # Чтение CSV и нормализация
│   │           ├── exporters.py  # CSV/XLSX экспорт
│   │           └── storage.py    # Сохранение импортированного набора
│   ├── migrations/           # Alembic-миграции
│   └── tests/                # Unit, API, integration, smoke
├── frontend/                 # React/Vite приложение
│   └── src/
│       ├── app/              # Провайдеры, роутер, конфиг API
│       ├── pages/            # Login, Register, Admin, Workspace, Profile
│       ├── widgets/          # Shell, top nav, результаты аналитики
│       ├── features/         # Формы и пользовательские сценарии
│       ├── entities/         # API-клиенты, схемы, query hooks
│       └── shared/           # UI-kit, api client, утилиты
├── task/                     # Тестовые обезличенные данные кейса
├── deploy/                   # Production entrypoint
├── Dockerfile                # Единый production-контейнер
├── amvera.yaml               # Конфигурация Amvera
├── prepare.cmd / prepare.sh  # Первичная подготовка окружения
└── dev.cmd / dev.sh          # Запуск локального dev-контура
```

---

## Локальное развертывание

### Требования

- Python **3.12+**
- Node.js **22 LTS** и npm
- Git Bash, WSL или Linux shell для запуска `.sh`-скриптов на Linux/macOS
- Для production-контура: Docker и PostgreSQL

### Быстрый старт на Windows

```powershell
prepare.cmd
dev.cmd
```

Скрипт подготовки создает `.venv`, устанавливает backend/frontend-зависимости, создает `.env` из примеров, применяет миграции и подготавливает роли. После запуска:

- frontend: `http://localhost:5173`
- backend API: `http://127.0.0.1:5000/api/v1`

Если виртуальное окружение было создано на другой ОС:

```powershell
prepare.cmd --force-venv
```

### Быстрый старт на Linux/macOS

```bash
chmod +x ./prepare.sh ./dev.sh
./prepare.sh
./dev.sh
```

### Создание администратора

Администратор нужен для импорта аналитических данных и управления пользователями.

Windows:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m flask --app wsgi create-admin
```

Linux/macOS:

```bash
PYTHONPATH=backend ./.venv/bin/python -m flask --app wsgi create-admin
```

После входа администратор открывает вкладку **«Источники данных»**, импортирует папку `task` или набор CSV-файлов и затем формирует выборки во вкладке **«Конструктор»**.

### Проверки

```powershell
.\.venv\Scripts\python.exe -m pytest backend

cd frontend
npm test
npm run build
```

---

## Production / Docker

```bash
docker build -t budget-constructor .
docker run -d --name budget-constructor \
  -p 8080:8080 \
  -e APP_ENV=production \
  -e SECRET_KEY=<long-random-secret> \
  -e DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname \
  -v "$(pwd)/data:/data" \
  --restart unless-stopped \
  budget-constructor
```

Production-контейнер:

- собирает `frontend/dist`;
- запускает Flask через Gunicorn на порту `8080`;
- применяет миграции при старте;
- хранит загружаемые файлы и изменяемые данные в `/data`;
- требует `DATABASE_URL`, если SQLite отключен.

Для Amvera уже подготовлены `Dockerfile`, `amvera.yaml` и `deploy/amvera-entrypoint.sh`. Обязательные переменные:

```text
SECRET_KEY=<long-random-secret>
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
```

Опционально для первого администратора:

```text
ADMIN_EMAIL=admin@example.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password>
```

---

## API

Все endpoints живут под `/api/v1`.

Ключевые группы:

- `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`
- `GET/PATCH /users/me`
- `GET /analytics/sources`
- `POST /analytics/import`
- `DELETE /analytics/import`
- `GET /analytics/import-issues`
- `GET /analytics/templates`
- `GET /analytics/metrics`
- `GET /analytics/search?q=...`
- `POST /analytics/query`
- `POST /analytics/timeline`
- `POST /analytics/compare`
- `POST /analytics/drilldown`
- `POST /analytics/export`
- `GET /assistant/health`, `POST /assistant/chat`, `POST /assistant/transcribe`
- `GET/POST/PATCH/DELETE /admin/users` для администраторов

Подробные контракты и правила расширения описаны в `docs/`.

---

## Команда

| Участник | Зона ответственности |
| --- | --- |
| **Самарин Александр** | Product, UI/UX, пользовательские сценарии, презентация решения |
| **Исаков Степан** | Архитектура, backend, frontend, ETL-логика, контейнеризация |

---

<div align="center">
  <i>Платформа превращает разрозненные бюджетные выгрузки в понятные аналитические выборки, которые можно получить без программирования, ручных сводных таблиц и долгой сверки кодов.</i>
</div>
