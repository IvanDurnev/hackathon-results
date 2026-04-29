# Структура фронтенд проекта

## 📁 Организация файлов

```
frontend/
├── src/
│   ├── pages/              # Страницы приложения
│   │   ├── Overview.jsx    # Страница обзора
│   │   ├── Constructor.jsx # Страница конструктора
│   │   ├── Analytics.jsx   # Страница аналитики
│   │   └── Documents.jsx   # Страница документов
│   ├── components/
│   │   ├── dashboard/      # Компоненты дашборда
│   │   ├── home/           # Компоненты главной страницы
│   │   ├── ui/             # Переиспользуемые UI компоненты
│   │   └── icons/          # SVG иконки
│   ├── constants/          # Константы приложения
│   ├── data/               # Mock данные
│   ├── utils/              # Утилиты
│   ├── App.jsx             # Главный компонент с навигацией
│   ├── main.jsx            # Точка входа
│   └── index.css           # Глобальные стили
├── public/                 # Статические файлы
└── package.json
```

## 🎯 Ключевые улучшения

### 1. Модульность
- Каждый компонент отвечает за одну задачу
- Легко тестировать и поддерживать
- Переиспользуемые UI компоненты

### 2. Разделение ответственности
- **pages/** - страницы приложения
- **components/** - визуальные компоненты
- **constants/** - статические данные
- **data/** - mock данные
- **utils/** - вспомогательные функции

### 3. Навигация
- Централизованное управление страницами в App.jsx
- Динамическое переключение через Sidebar
- Автоматическое обновление заголовков и breadcrumbs

### 4. Чистота кода
- Удалены все пустые файлы
- Убраны неиспользуемые импорты
- Нет дублирования кода

### 5. Масштабируемость
- Легко добавлять новые страницы
- Понятная структура папок
- Централизованное управление данными

## 🚀 Использование

### Добавление новой страницы

1. Создайте компонент в `src/pages/`:
```jsx
export default function NewPage() {
  return <div>Новая страница</div>;
}
```

2. Добавьте в `App.jsx`:
```jsx
import NewPage from './pages/NewPage';

const PAGES = {
  // ...
  newpage: { 
    component: NewPage, 
    title: 'Новая страница', 
    breadcrumbs: ['Система', 'Новая'] 
  }
};
```

3. Добавьте ссылку в sidebar:
```jsx
const sidebarLinks = [
  // ...
  { label: "Новая", icon: <Icon />, page: 'newpage' }
];
```

### Компоненты дашборда
```jsx
import Sidebar from './components/dashboard/Sidebar';
import Header from './components/dashboard/Header';
import MetricsGrid from './components/dashboard/MetricsGrid';
```

### UI компоненты
```jsx
import Button from './components/ui/Button';
import Input from './components/ui/Input';
import Select from './components/ui/Select';
import RadioGroup from './components/ui/RadioGroup';
```

### Константы
```jsx
import { METRICS_DATA, DEPARTMENTS } from './constants/dashboard';
```

## 📝 Соглашения

1. Компоненты именуются в PascalCase
2. Файлы компонентов имеют расширение .jsx
3. Константы в UPPER_SNAKE_CASE
4. Утилиты в camelCase
5. Один компонент = один файл
6. Страницы в папке pages/

