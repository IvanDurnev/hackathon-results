from flask import Blueprint, Flask


def register_api(app: Flask) -> None:
    from app.modules.admin.routes import bp as admin_bp
    from app.modules.assistant.routes import bp as assistant_bp
    from app.modules.budget_constructor.routes import bp as analytics_bp
    from app.modules.auth.routes import bp as auth_bp
    from app.modules.files.routes import bp as files_bp
    from app.modules.users.routes import bp as users_bp

    api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

    @api_v1_bp.get("/health")
    def health():
        return {"status": "ok"}

    api_v1_bp.register_blueprint(auth_bp, url_prefix="/auth")
    api_v1_bp.register_blueprint(users_bp, url_prefix="/users")
    api_v1_bp.register_blueprint(files_bp, url_prefix="/files")
    api_v1_bp.register_blueprint(analytics_bp, url_prefix="/analytics")
    api_v1_bp.register_blueprint(assistant_bp, url_prefix="/assistant")
    api_v1_bp.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_v1_bp)
