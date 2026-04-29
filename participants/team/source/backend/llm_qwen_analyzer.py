"""
Модуль для анализа контента с помощью QWEN API с fallback на Ollama
"""

import requests
import json
import os
from typing import Dict, List, Optional
import asyncio
from datetime import datetime

class QwenLLMAnalyzer:
    """Анализатор контента на основе QWEN API с fallback на Ollama"""
    
    def __init__(self, qwen_token: str = None):
        # QWEN API настройки
        self.qwen_token = qwen_token or os.getenv("QWEN_TOKEN")
        self.qwen_api_url = "https://api.aicloud.sbercloud.ru/public/v2/llm/v1/chat/completions"
        
        # Ollama настройки (fallback)
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:latest")
        
        # Статус API
        self.qwen_available = self._check_qwen_availability()
        
        if self.qwen_available:
            print("✅ QWEN API доступен")
        else:
            print("⚠️ QWEN API недоступен, используется Ollama")
    
    def _check_qwen_availability(self) -> bool:
        """Проверка доступности QWEN API"""
        if not self.qwen_token:
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.qwen_token}",
                "Content-Type": "application/json"
            }
            
            # Простой тестовый запрос
            test_data = {
                "model": "Qwen/Qwen2.5-72B-Instruct",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.qwen_api_url,
                headers=headers,
                json=test_data,
                timeout=5
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"QWEN API проверка не удалась: {e}")
            return False
    
    def get_system_prompt(self, tone: str, slide_count: int) -> str:
        """Генерация системного промпта для LLM"""
        
        tone_guide = {
            'official': '''
            - Используй формальный деловой язык
            - Акцент на фактах, цифрах и аналитике
            - Структурированность и четкость
            - Профессиональная терминология
            - Консервативный подход к визуализации
            ''',
            'creative': '''
            - Используй более живой и динамичный язык
            - Баланс между фактами и storytelling
            - Креативные метафоры и аналогии
            - Эмоциональный резонанс с аудиторией
            - Яркие визуальные образы
            '''
        }
        
        return f"""Ты — эксперт по созданию профессиональных бизнес-презентаций и работаешь в команде Ростелекома.

ТВОЯ ЗАДАЧА:
Проанализировать предоставленный текст и создать структуру презентации из {slide_count} слайдов.

ТОН ПРЕЗЕНТАЦИИ: {tone}
{tone_guide.get(tone, tone_guide['official'])}

ПРИНЦИПЫ СОЗДАНИЯ СЛАЙДОВ:

1. СТРУКТУРА
   - Титульный слайд (1)
   - Введение/Проблематика (1-2 слайда)
   - Основной контент (разбить на логические блоки)
   - Выводы/Рекомендации (1 слайд)
   - Призыв к действию (1 слайд)

2. КОНТЕНТ СЛАЙДА
   - Заголовок: Четкий, емкий (макс. 8-10 слов)
   - Буллеты: 3-5 ключевых пунктов
   - Каждый буллет: 1-2 строки
   - Избегай перегрузки информацией

3. ВИЗУАЛИЗАЦИЯ
   - Определи, где нужны изображения/графики
   - Создай промпты для генерации релевантных изображений
   - Промпт должен быть на английском, описательным и специфичным

4. ЛЕЙАУТЫ
   - title_only: Только заголовок (титульный, разделители)
   - title_content: Заголовок + буллеты (основной контент)
   - title_image: Заголовок + изображение
   - two_column: Две колонки контента

ФОРМАТ ОТВЕТА:
Верни ТОЛЬКО валидный JSON по следующей схеме (без дополнительного текста):

{{
  "presentation": {{
    "title": "Название презентации",
    "subtitle": "Подзаголовок",
    "tone": "{tone}",
    "slides": [
      {{
        "id": 1,
        "type": "title",
        "layout": "title_only",
        "title": "Заголовок",
        "subtitle": "Подзаголовок",
        "content": {{"bullets": [], "text": ""}},
        "image_prompt": null
      }},
      {{
        "id": 2,
        "type": "content",
        "layout": "title_content",
        "title": "Конкретный заголовок с месседжем",
        "content": {{
          "bullets": [
            "Краткий пункт с цифрами или фактами",
            "Второй пункт, развивающий тему",
            "Третий пункт с выводом или действием"
          ],
          "text": ""
        }},
        "image_prompt": "Detailed English prompt if visual needed"
      }}
    ]
  }}
}}

ВАЖНО:
- Анализируй глубоко - не просто переписывай текст
- Выделяй главное - отбрасывай второстепенное
- Структурируй логично - создавай narrative flow
- Добавляй инсайты - показывай "So what?"
- Визуализируй данные - где нужны графики/диаграммы

НАЧИНАЙ АНАЛИЗ!
"""

    async def analyze_with_qwen(
        self, 
        content: str, 
        tone: str = "official", 
        slide_count: int = 10
    ) -> Optional[Dict]:
        """Анализ контента через QWEN API"""
        
        headers = {
            "Authorization": f"Bearer {self.qwen_token}",
            "Content-Type": "application/json"
        }
        
        system_prompt = self.get_system_prompt(tone, slide_count)
        
        user_message = f"""Проанализируй следующий текст и создай структуру презентации:

{content}

Требования:
- Количество слайдов: {slide_count}
- Тон: {tone}

Верни ТОЛЬКО JSON структуру презентации."""

        data = {
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 8000,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            response = await asyncio.to_thread(
                requests.post,
                self.qwen_api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Извлечение текста ответа
                if "choices" in result and len(result["choices"]) > 0:
                    response_text = result["choices"][0]["message"]["content"]
                    
                    # Попытка найти JSON в ответе
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        presentation_data = json.loads(json_str)
                        
                        # Валидация структуры
                        if self._validate_structure(presentation_data):
                            return presentation_data
                        else:
                            print("⚠️ Невалидная структура от QWEN")
                            return None
                    else:
                        print("⚠️ JSON не найден в ответе QWEN")
                        return None
            else:
                print(f"⚠️ QWEN API ошибка: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка при обращении к QWEN API: {str(e)}")
            return None
    
    async def analyze_with_ollama(
        self, 
        content: str, 
        tone: str = "official", 
        slide_count: int = 10
    ) -> Optional[Dict]:
        """Анализ контента через локальную Ollama"""
        
        system_prompt = self.get_system_prompt(tone, slide_count)
        
        user_message = f"""Проанализируй следующий текст и создай структуру презентации:

{content}

Требования:
- Количество слайдов: {slide_count}
- Тон: {tone}

Верни ТОЛЬКО JSON структуру презентации."""

        data = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 8000
            }
        }
        
        try:
            response = await asyncio.to_thread(
                requests.post,
                f"{self.ollama_url}/api/chat",
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("message", {}).get("content", "")
                
                # Попытка найти JSON в ответе
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    presentation_data = json.loads(json_str)
                    
                    # Валидация структуры
                    if self._validate_structure(presentation_data):
                        return presentation_data
                    else:
                        print("⚠️ Невалидная структура от Ollama")
                        return None
                else:
                    print("⚠️ JSON не найден в ответе Ollama")
                    return None
            else:
                print(f"⚠️ Ollama API ошибка: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка при обращении к Ollama: {str(e)}")
            return None
    
    async def analyze_content(
        self, 
        content: str, 
        tone: str = "official", 
        slide_count: int = 10,
        include_images: bool = True
    ) -> Dict:
        """
        Универсальный метод анализа с автоматическим fallback
        
        Args:
            content: Текст для анализа
            tone: Тон презентации (official/creative)
            slide_count: Количество слайдов
            include_images: Включать ли промпты для изображений
            
        Returns:
            Структура презентации в формате JSON
        """
        
        # Попытка 1: QWEN API
        if self.qwen_available:
            print("🔄 Попытка генерации через QWEN API...")
            result = await self.analyze_with_qwen(content, tone, slide_count)
            
            if result:
                print("✅ Успешная генерация через QWEN API")
                return result
            else:
                print("⚠️ QWEN API не вернул результат, переключаюсь на Ollama...")
        
        # Попытка 2: Ollama (fallback)
        print("🔄 Попытка генерации через Ollama...")
        result = await self.analyze_with_ollama(content, tone, slide_count)
        
        if result:
            print("✅ Успешная генерация через Ollama")
            return result
        
        # Если оба метода не сработали - генерируем mock данные
        print("⚠️ Оба API недоступны, генерируются mock данные...")
        return self._generate_mock_presentation(content, tone, slide_count)
    
    def _validate_structure(self, data: Dict) -> bool:
        """Валидация структуры презентации"""
        
        if 'presentation' not in data:
            return False
        
        presentation = data['presentation']
        
        required_fields = ['title', 'slides']
        if not all(field in presentation for field in required_fields):
            return False
        
        if not isinstance(presentation['slides'], list) or len(presentation['slides']) == 0:
            return False
        
        # Проверка каждого слайда
        for slide in presentation['slides']:
            required_slide_fields = ['id', 'type', 'layout', 'title']
            if not all(field in slide for field in required_slide_fields):
                return False
        
        return True
    
    def _generate_mock_presentation(self, content: str, tone: str, slide_count: int) -> Dict:
        """Генерация mock презентации (fallback)"""
        
        slides = []
        
        # Титульный слайд
        slides.append({
            "id": 1,
            "type": "title",
            "layout": "title_only",
            "title": "Презентация по материалам документа",
            "subtitle": f"Сгенерировано автоматически • {datetime.now().strftime('%d.%m.%Y')}",
            "content": {"bullets": [], "text": ""}
        })
        
        # Контентные слайды
        for i in range(2, slide_count + 1):
            slides.append({
                "id": i,
                "type": "conclusion" if i == slide_count else "content",
                "layout": "title_content",
                "title": f"Ключевой раздел {i}",
                "content": {
                    "bullets": [
                        "Анализ текущей ситуации на рынке",
                        "Выявление ключевых трендов и возможностей",
                        "Разработка стратегии внедрения",
                        "Оценка рисков и планирование ресурсов"
                    ],
                    "text": ""
                },
                "image_prompt": "Modern business analytics, professional style" if i % 3 == 0 else None
            })
        
        return {
            "presentation": {
                "title": "Презентация",
                "subtitle": "Mock данные",
                "tone": tone,
                "slides": slides
            }
        }
    
    def sync_analyze_content(self, content: str, tone: str = "official", 
                            slide_count: int = 10, include_images: bool = True) -> Dict:
        """Синхронная обертка для analyze_content"""
        return asyncio.run(
            self.analyze_content(content, tone, slide_count, include_images)
        )


# Пример использования
if __name__ == "__main__":
    # Инициализация с токеном QWEN
    qwen_token = "eyJhbGciOiJIUzM4NCJ9.eyJzY29wZXMiOlsibGxhbWEiLCJzZCIsInlhQXJ0Il0sInN1YiI6ImhhY2thdGhvbl8yNl8wMyIsImlhdCI6MTc3Njk0OTA0NCwiZXhwIjoxNzc3NjQwMjQ0fQ.gbftSKsqE3bf6aH6DqBLKeWQW6yyk4RpAAaMxlHIHkyzioqCufFjOIgq0FioiQv9"
    
    analyzer = QwenLLMAnalyzer(qwen_token=qwen_token)
    
    # Тестовый контент
    test_content = """
    Отчёт о внедрении AI системы в Q4 2025
    
    Ключевые достижения:
    - Автоматизация 70% рутинных задач
    - Снижение времени обработки с 4 часов до 15 минут
    - Точность предсказаний AI: 94%
    - ROI достигнут за 3 месяца
    """
    
    # Генерация презентации
    result = analyzer.sync_analyze_content(
        content=test_content,
        tone="official",
        slide_count=10,
        include_images=True
    )
    
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТ:")
    print("="*50)
    print(json.dumps(result, ensure_ascii=False, indent=2))
