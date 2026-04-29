# backend/image_service.py

import os
import uuid
import requests


class ImageService:
    """
    Image search service via Pexels API

    Flow:
    prompt → search image → download → save local file
    """

    def __init__(self):
        self.base_url = "https://api.pexels.com/v1/search"
        self.api_key = os.getenv("PEXELS_API_KEY")

        if not self.api_key:
            raise ValueError(
                "PEXELS_API_KEY not found in environment variables"
            )

        self.headers = {
            "Authorization": self.api_key
        }

    def enhance_prompt(self, prompt: str) -> str:
        """
        Улучшаем запрос для красивых presentation-style картинок
        """

        return (
            f"{prompt}, modern business presentation, "
            f"flat illustration, startup style, clean design"
        )

    def search_image(self, prompt: str):
        """
        Ищем изображение через Pexels API
        """

        enhanced_query = self.enhance_prompt(prompt)

        params = {
            "query": enhanced_query,
            "per_page": 1,
            "orientation": "landscape",
            "size": "large"
        }

        response = requests.get(
            self.base_url,
            headers=self.headers,
            params=params,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("photos"):
            raise Exception(
                f"No images found for prompt: {prompt}"
            )

        import random

        photos = data["photos"][:8]

        selected = random.choice(photos)

        image_url = selected["src"]["large2x"]

        return image_url

    def download_image(
        self,
        image_url: str,
        save_path: str = None
    ):
        """
        Скачиваем найденное изображение
        """

        if not save_path:
            filename = f"pexels_{uuid.uuid4().hex[:10]}.jpg"
            save_path = filename

        response = requests.get(
            image_url,
            timeout=120
        )

        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)

        return save_path

    def generate_and_download(
        self,
        prompt: str,
        aspect: str = "16:9",
        use_yandex_art: bool = True
    ):
        """
        Совместимость со старым pipeline:
        generate_and_download(...) остаётся тем же методом
        """

        try:
            print(f"[PEXELS] Searching image for: {prompt}")

            image_url = self.search_image(prompt)

            print(f"[PEXELS] Found image: {image_url}")

            file_path = self.download_image(image_url)

            print(f"[PEXELS] Downloaded image: {file_path}")

            return file_path

        except Exception as e:
            print(f"[PEXELS ERROR] {str(e)}")
            raise e