from typing import Any

from flask import jsonify
from pydantic import BaseModel


def to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    return value


def json_response(payload: Any, status: int = 200):
    return jsonify(to_jsonable(payload)), status


def message_response(message: str, status: int = 200):
    return json_response({"message": message}, status)


def error_response(
    code: str,
    message: str,
    status: int,
    details: dict | None = None,
):
    return json_response(
        {
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
        status,
    )


def paginated_response(items: list[Any], pagination: dict[str, int]):
    return json_response({"items": items, "pagination": pagination})
