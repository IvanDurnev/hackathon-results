class AppError(Exception):
    status_code = 400
    code = "application_error"
    message = "Ошибка приложения."

    def __init__(self, message: str | None = None, details: dict | None = None):
        super().__init__(message or self.message)
        self.message = message or self.message
        self.details = details or {}


class ValidationAppError(AppError):
    status_code = 422
    code = "validation_error"
    message = "Запрос не прошел проверку."


class AuthenticationRequired(AppError):
    status_code = 401
    code = "authentication_required"
    message = "Требуется авторизация."


class PermissionDenied(AppError):
    status_code = 403
    code = "permission_denied"
    message = "У вас нет доступа к этому ресурсу."


class ResourceNotFound(AppError):
    status_code = 404
    code = "not_found"
    message = "Ресурс не найден."


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
    message = "Ресурс уже существует."
