import aiohttp
import uuid
import asyncio
from typing import Optional


class ImageService:
    def __init__(self, api_key: str, api_url: str = "https://ai.rt.ru/api/1.0/ya/image"):
        self.api_key = api_key
        self.api_url = api_url
        self.download_url = "https://ai.rt.ru/api/1.0/download"

    async def generate_image(self, prompt: str, aspect: str = "16:9") -> Optional[str]:
        """Generate image using Yandex ART and return download URL"""

        # Step 1: Request image generation
        request_uuid = str(uuid.uuid4())

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "uuid": request_uuid,
                "image": {
                    "request": prompt,
                    "seed": hash(prompt) % 1000000000,  # Generate seed from prompt
                    "translate": False,
                    "model": "yandex-art",
                    "aspect": aspect
                }
            }

            try:
                # Send generation request
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result and len(result) > 0:
                            message_id = result[0].get("message", {}).get("id")

                            if message_id:
                                # Wait a bit for generation to complete
                                await asyncio.sleep(2)

                                # Step 2: Download the generated image
                                return await self._download_image(message_id)
                    else:
                        print(f"Image generation API error: {response.status}")
                        return None

            except Exception as e:
                print(f"Image service error: {e}")
                return None

        return None

    async def _download_image(self, message_id: int, image_type: str = "png") -> Optional[str]:
        """Download generated image and return base64 or save locally"""

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            download_url = f"{self.download_url}?id={message_id}&serviceType=yaArt&imageType={image_type}"

            try:
                async with session.get(download_url, headers=headers) as response:
                    if response.status == 200:
                        # Return image as base64 for embedding
                        import base64
                        image_data = await response.read()
                        image_base64 = base64.b64encode(image_data).decode('utf-8')
                        return f"data:image/{image_type};base64,{image_base64}"
                    else:
                        print(f"Image download error: {response.status}")
                        return None
            except Exception as e:
                print(f"Download error: {e}")
                return None

    async def get_available_aspects(self) -> list:
        """Get available aspect ratios for images"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            try:
                async with session.get("https://ai.rt.ru/api/1.0/ya/aspect", headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return [item.get("code") for item in result]
            except Exception as e:
                print(f"Failed to get aspects: {e}")

            return ["16:9", "4:3", "1:1"]  # Default aspects