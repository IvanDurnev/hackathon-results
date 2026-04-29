import httpx
import io
from pathlib import Path
from PIL import Image

CACHE_DIR = Path("./tmp/cache")

async def download_image(url: str) -> io.BytesIO | None:
    try:
        if url.startswith("/"):
            file_path = CACHE_DIR / url.replace("/images/", "")
            if file_path.exists():
                return io.BytesIO(file_path.read_bytes())
            return None
        
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return io.BytesIO(resp.content)
    except Exception as e:
        print(f"⚠️ Ошибка загрузки изображения: {e}")
        return None

def resize_image(img_stream: io.BytesIO, max_width: int = 500, max_height: int = 500) -> io.BytesIO:
    img = Image.open(img_stream)
    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output
