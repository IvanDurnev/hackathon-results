from http import HTTPStatus

from flask import Flask
from flask_login import LoginManager
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.core.errors import AppError
from app.core.responses import error_response
from app.extensions import db, login_manager


def register_error_handlers(app: Flask) -> None:
    register_login_errors(login_manager)

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return error_response(
            error.code,
            error.message,
            error.status_code,
            error.details,
        )

    @app.errorhandler(ValidationError)
    def handle_pydantic_error(error: ValidationError):
        return error_response(
            "validation_error",
            "Запрос не прошел проверку.",
            422,
            {"fields": error.errors(include_url=False, include_context=False)},
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        code = HTTPStatus(error.code).name.lower() if error.code else "http_error"
        return error_response(code, "Ошибка запроса.", error.code or 500)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        if app.config.get("TESTING"):
            raise error
        db.session.rollback()
        return error_response("internal_error", "Внутренняя ошибка сервера.", 500)


def register_login_errors(manager: LoginManager) -> None:
    @manager.unauthorized_handler
    def unauthorized():
        return error_response(
            "authentication_required",
            "Требуется авторизация.",
            401,
        )
