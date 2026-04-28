import os
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class Config:
    """Base configuration class"""

    # API Configuration
    API_TOKEN: str = os.getenv("ROSTELECOM_API_TOKEN", "")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://ai.rt.ru/api/1.0")

    # LLM Service (Leopold)
    LLAMA_API_URL: str = os.getenv("LLAMA_API_URL", f"{API_BASE_URL}/llama/chat")
    LLAMA_MODEL: str = os.getenv("LLAMA_MODEL", "Qwen/Qwen2.5-72B-Instruct")
    LLAMA_MAX_TOKENS: int = int(os.getenv("LLAMA_MAX_TOKENS", "4096"))
    LLAMA_TEMPERATURE: float = float(os.getenv("LLAMA_TEMPERATURE", "0.3"))

    # Image Service (Yandex ART)
    YANDEX_ART_API_URL: str = os.getenv("YANDEX_ART_API_URL", f"{API_BASE_URL}/ya/image")
    YANDEX_ART_DOWNLOAD_URL: str = os.getenv("YANDEX_ART_DOWNLOAD_URL", f"{API_BASE_URL}/download")
    YANDEX_ART_ASPECT_URL: str = os.getenv("YANDEX_ART_ASPECT_URL", f"{API_BASE_URL}/ya/aspect")
    DEFAULT_IMAGE_ASPECT: str = os.getenv("DEFAULT_IMAGE_ASPECT", "16:9")
    IMAGE_GENERATION_TIMEOUT: int = int(os.getenv("IMAGE_GENERATION_TIMEOUT", "30"))

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"

    # File Storage
    GENERATED_FILES_DIR: str = os.getenv("GENERATED_FILES_DIR", "generated_files")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    MAX_DOCUMENT_CHARS: int = int(os.getenv("MAX_DOCUMENT_CHARS", "10000"))

    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.API_TOKEN:
            raise ValueError("ROSTELECOM_API_TOKEN is not set in environment variables")
        return True

    @classmethod
    def get_api_headers(cls) -> dict:
        """Get common API headers"""
        return {
            "Authorization": f"Bearer {cls.API_TOKEN}",
            "Content-Type": "application/json"
        }


class DevelopmentConfig(Config):
    """Development configuration"""
    RELOAD = True
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    RELOAD = False
    DEBUG = False
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://yourdomain.com").split(",")


# Select configuration based on environment
ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "production":
    config = ProductionConfig()
else:
    config = DevelopmentConfig()