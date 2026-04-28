import json
import aiohttp
import uuid
from typing import List, Dict, Optional
from backend.app.models import PresentationRequest, SlideContent


class LLMService:
    def __init__(self, api_key: str, api_url: str = "https://ai.rt.ru/api/1.0/llama/chat"):
        self.api_key = api_key
        self.api_url = api_url

    async def generate_presentation_structure(
            self,
            request: PresentationRequest,
            document_content: str = ""
    ) -> List[SlideContent]:
        """Generate presentation structure using LLM (Leopold)"""

        prompt = self._build_prompt(request, document_content)

        # Generate UUID for request
        request_uuid = str(uuid.uuid4())

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "uuid": request_uuid,
                "chat": {
                    "model": "Qwen/Qwen2.5-72B-Instruct",
                    "user_message": prompt,
                    "contents": [],
                    "message_template": "<s>{role}\n{content}</s>",
                    "response_template": "<s>bot\n",
                    "system_prompt": """Ты - профессиональный дизайнер презентаций и эксперт по структурированию информации. 
                    Твоя задача - создавать четкие, логичные презентации на русском языке.
                    Отвечай только в формате JSON.""",
                    "max_new_tokens": 4096,
                    "no_repeat_ngram_size": 15,
                    "repetition_penalty": 1.1,
                    "temperature": 0.3,
                    "top_k": 40,
                    "top_p": 0.9,
                    "chat_history": []
                }
            }

            try:
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Parse response from Leopold
                        if result and len(result) > 0:
                            content = result[0].get("message", {}).get("content", "")
                            # Extract JSON from response
                            slides_data = self._extract_json(content)

                            slides = []
                            for slide in slides_data.get("slides", []):
                                slides.append(SlideContent(
                                    title=slide.get("title", "Без названия"),
                                    content=slide.get("content", ""),
                                    image_prompt=slide.get("image_prompt", "")
                                ))

                            return slides
                    else:
                        print(f"LLM API error: {response.status}")
                        return self._get_fallback_structure(request)

            except Exception as e:
                print(f"LLM service error: {e}")
                return self._get_fallback_structure(request)

        return self._get_fallback_structure(request)

    def _extract_json(self, content: str) -> dict:
        """Extract JSON from LLM response"""
        try:
            # Try to find JSON in response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass

        # Return default structure
        return {
            "slides": [
                {"title": "Презентация", "content": "Содержание презентации", "image_prompt": ""}
            ]
        }

    def _build_prompt(self, request: PresentationRequest, document_content: str) -> str:
        prompt = f"""Создай презентацию на {request.num_slides} слайдов.

Тема: {request.prompt}

Стиль оформления: {request.style.value}
Тон повествования: {request.tone.value}
"""

        if document_content:
            prompt += f"\n\nСодержание документа для анализа:\n{document_content[:6000]}\n"

        prompt += """

Ответ должен быть в строгом формате JSON:
{
    "slides": [
        {
            "title": "Заголовок слайда",
            "content": "Основное содержание слайда (используй \\n для переноса строк, маркированные списки)",
            "image_prompt": "Описание для генерации изображения на русском языке"
        }
    ]
}

Требования:
1. Первый слайд - титульный
2. Каждый слайд должен содержать ключевую мысль
3. Используй маркированные списки для улучшения читаемости
4. Image prompt должен быть детальным описанием на русском языке
5. Общий объем: примерно 2-3 предложения на слайд

Создай презентацию в указанном JSON формате:"""

        return prompt

    def _get_fallback_structure(self, request: PresentationRequest) -> List[SlideContent]:
        """Return fallback structure if API fails"""
        slides = []

        # Title slide
        slides.append(SlideContent(
            title=request.prompt,
            content="Презентация",
            image_prompt="Профессиональный фон для презентации"
        ))

        # Content slides
        for i in range(request.num_slides - 1):
            slides.append(SlideContent(
                title=f"Ключевой аспект {i + 1}",
                content="• Важный пункт\n• Второй важный пункт\n• Третий пункт",
                image_prompt="Иллюстрация к теме презентации"
            ))

        return slides

    async def process_document(self, file_content: bytes, filename: str) -> str:
        """Extract text from uploaded document"""
        if filename.lower().endswith('.pdf'):
            from PyPDF2 import PdfReader
            import io
            try:
                reader = PdfReader(io.BytesIO(file_content))
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text[:10000]  # Limit length
            except Exception as e:
                print(f"PDF processing error: {e}")
                return ""

        elif filename.lower().endswith('.docx'):
            from docx import Document
            import io
            try:
                doc = Document(io.BytesIO(file_content))
                text = "\n".join([para.text for para in doc.paragraphs])
                return text[:10000]
            except Exception as e:
                print(f"DOCX processing error: {e}")
                return ""

        return ""