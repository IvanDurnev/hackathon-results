import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
DEFAULT_AMVERA_DATA_DIR = Path("/data")

load_dotenv(REPO_ROOT / ".env")
load_dotenv(BACKEND_DIR / ".env", override=True)


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def env_list(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def running_on_amvera() -> bool:
    return os.getenv("AMVERA") == "1"


def sqlite_disabled() -> bool:
    return running_on_amvera() or os.getenv("DISABLE_SQLITE", "0").lower() in {"1", "true", "yes", "on"}


def default_data_dir() -> Path:
    configured_data_dir = os.getenv("DATA_DIR")
    if configured_data_dir:
        return Path(configured_data_dir)
    if running_on_amvera():
        return DEFAULT_AMVERA_DATA_DIR
    return BACKEND_DIR / "instance"


def default_database_uri(database_name: str = "app.sqlite3") -> str:
    configured_url = os.getenv("DATABASE_URL")
    if configured_url:
        return normalize_database_url(configured_url)
    if sqlite_disabled():
        raise RuntimeError("DATABASE_URL must be set when SQLite is disabled.")
    return f"sqlite:///{default_data_dir() / database_name}"


def sqlite_database_uri(data_dir: Path, database_name: str = "app.sqlite3") -> str:
    return f"sqlite:///{data_dir / database_name}"


def default_upload_folder() -> str:
    return str(default_data_dir() / "uploads")


class BaseConfig:
    APP_NAME = os.getenv("APP_NAME", "Hackathon Starter")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    DATA_DIR = str(default_data_dir())
    FRONTEND_DIST_DIR = os.getenv("FRONTEND_DIST_DIR", str(REPO_ROOT / "frontend" / "dist"))
    SQLALCHEMY_DATABASE_URI = default_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JSON_SORT_KEYS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_PROTECTION = os.getenv("SESSION_PROTECTION", "basic")
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = os.getenv("REMEMBER_COOKIE_SAMESITE", "Lax")

    ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "20"))
    MAX_PER_PAGE = int(os.getenv("MAX_PER_PAGE", "100"))
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", default_upload_folder())
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(512 * 1024 * 1024)))
    ANALYTICS_AUTO_IMPORT = os.getenv("ANALYTICS_AUTO_IMPORT", "0") == "1"
    AI_MODULE_URL = os.getenv("AI_MODULE_URL", "http://127.0.0.1:8091/api/ai")
    AI_MODULE_API_KEY = os.getenv("AI_MODULE_API_KEY", "")
    AI_MODULE_TIMEOUT_SECONDS = float(os.getenv("AI_MODULE_TIMEOUT_SECONDS", "60"))
    AI_MODULE_STT_MODEL = os.getenv("AI_MODULE_STT_MODEL", "")
    AI_MODULE_STT_LANGUAGE = os.getenv("AI_MODULE_STT_LANGUAGE", "ru")
    CORS_ORIGINS = env_list(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )

    @staticmethod
    def init_app(app):
        if os.getenv("APP_NAME"):
            app.config["APP_NAME"] = os.getenv("APP_NAME")
        if os.getenv("SECRET_KEY"):
            app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
        if os.getenv("DATA_DIR"):
            app.config["DATA_DIR"] = os.getenv("DATA_DIR")
        data_dir = Path(app.config["DATA_DIR"])
        if not data_dir.is_absolute():
            data_dir = REPO_ROOT / data_dir
        app.config["DATA_DIR"] = str(data_dir.resolve())
        if os.getenv("DATABASE_URL"):
            app.config["SQLALCHEMY_DATABASE_URI"] = normalize_database_url(os.getenv("DATABASE_URL", ""))
        elif sqlite_disabled():
            raise RuntimeError("DATABASE_URL must be set when SQLite is disabled.")
        elif os.getenv("DATA_DIR"):
            app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_database_uri(data_dir)
        if os.getenv("ITEMS_PER_PAGE"):
            app.config["ITEMS_PER_PAGE"] = int(os.getenv("ITEMS_PER_PAGE", "20"))
        if os.getenv("MAX_PER_PAGE"):
            app.config["MAX_PER_PAGE"] = int(os.getenv("MAX_PER_PAGE", "100"))
        if os.getenv("MAX_CONTENT_LENGTH"):
            app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", str(512 * 1024 * 1024)))
        if os.getenv("UPLOAD_FOLDER"):
            app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")
        if os.getenv("CORS_ORIGINS") is not None:
            app.config["CORS_ORIGINS"] = env_list("CORS_ORIGINS")
        if os.getenv("FRONTEND_DIST_DIR"):
            app.config["FRONTEND_DIST_DIR"] = os.getenv("FRONTEND_DIST_DIR")
        if os.getenv("AI_MODULE_URL"):
            app.config["AI_MODULE_URL"] = os.getenv("AI_MODULE_URL")
        if os.getenv("AI_MODULE_API_KEY"):
            app.config["AI_MODULE_API_KEY"] = os.getenv("AI_MODULE_API_KEY")
        if os.getenv("AI_MODULE_TIMEOUT_SECONDS"):
            app.config["AI_MODULE_TIMEOUT_SECONDS"] = float(os.getenv("AI_MODULE_TIMEOUT_SECONDS", "60"))
        if os.getenv("AI_MODULE_STT_MODEL"):
            app.config["AI_MODULE_STT_MODEL"] = os.getenv("AI_MODULE_STT_MODEL")
        if os.getenv("AI_MODULE_STT_LANGUAGE"):
            app.config["AI_MODULE_STT_LANGUAGE"] = os.getenv("AI_MODULE_STT_LANGUAGE")

        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        Path(app.config["DATA_DIR"]).mkdir(parents=True, exist_ok=True)
        upload_folder = Path(app.config["UPLOAD_FOLDER"])
        if not upload_folder.is_absolute():
            upload_folder = REPO_ROOT / upload_folder
        app.config["UPLOAD_FOLDER"] = str(upload_folder.resolve())
        Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
        frontend_dist = Path(app.config["FRONTEND_DIST_DIR"])
        if not frontend_dist.is_absolute():
            frontend_dist = REPO_ROOT / frontend_dist
        app.config["FRONTEND_DIST_DIR"] = str(frontend_dist.resolve())


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CORS_ORIGINS = []


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    @staticmethod
    def init_app(app):
        BaseConfig.init_app(app)
        if not os.getenv("SECRET_KEY"):
            raise RuntimeError("SECRET_KEY must be set in production.")


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
