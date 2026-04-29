import os
from pathlib import Path

from flask import Flask, abort, send_from_directory
from flask_cors import CORS
from werkzeug.security import safe_join

from app.api.v1.errors import register_error_handlers
from app.api.v1.routes import register_api
from app.config import CONFIGS, DevelopmentConfig
from app.extensions import db, login_manager, migrate


def create_app(config_name: str | None = None, config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    selected_config = config_name or os.getenv("APP_ENV", "development")
    config_class = CONFIGS.get(selected_config, DevelopmentConfig)

    app.config.from_object(config_class)
    config_class.init_app(app)

    if config_overrides:
        app.config.update(config_overrides)

    register_extensions(app)
    register_models()
    register_api(app)
    register_error_handlers(app)
    register_cli(app)
    register_frontend(app)

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.session_protection = app.config.get("SESSION_PROTECTION", "basic")
    login_manager.init_app(app)

    from app.modules.auth.models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    origins = app.config.get("CORS_ORIGINS", [])
    if origins:
        CORS(
            app,
            resources={r"/api/.*": {"origins": origins}},
            supports_credentials=True,
        )


def register_models() -> None:
    from app.modules.auth import models as auth_models  # noqa: F401
    from app.modules.budget_constructor import models as budget_constructor_models  # noqa: F401
    from app.modules.files import models as file_models  # noqa: F401


def register_cli(app: Flask) -> None:
    from app.cli.commands import register_commands

    register_commands(app)


def register_frontend(app: Flask) -> None:
    frontend_dist = Path(app.config["FRONTEND_DIST_DIR"])
    index_file = frontend_dist / "index.html"
    if not index_file.is_file():
        return

    @app.get("/")
    def frontend_index():
        return send_from_directory(frontend_dist, "index.html")

    @app.get("/<path:path>")
    def frontend_static_or_spa(path: str):
        if path.startswith("api/"):
            abort(404)

        safe_path = safe_join(str(frontend_dist), path)
        if safe_path and Path(safe_path).is_file():
            return send_from_directory(frontend_dist, path)

        return send_from_directory(frontend_dist, "index.html")
