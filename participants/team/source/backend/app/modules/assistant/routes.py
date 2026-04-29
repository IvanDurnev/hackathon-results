from __future__ import annotations

from flask import Blueprint, request

from app.core.permissions import auth_required
from app.core.responses import json_response
from app.core.security import json_payload
from app.modules.assistant.schemas import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantHealthResponse,
    AssistantTranscriptionResponse,
)
from app.modules.assistant.services import assistant_health, ask_assistant, transcribe_audio

bp = Blueprint("assistant", __name__)


@bp.get("/health")
@auth_required
def health():
    return json_response(AssistantHealthResponse(**assistant_health()).model_dump())


@bp.post("/chat")
@auth_required
def chat():
    data = AssistantChatRequest.model_validate(json_payload())
    response = ask_assistant(
        prompt=data.prompt,
        messages=[message.model_dump() for message in data.messages],
        context=data.context,
    )
    return json_response(AssistantChatResponse(**response).model_dump())


@bp.post("/transcribe")
@auth_required
def transcribe():
    uploaded = request.files.get("file") or request.files.get("audio")
    if uploaded is None:
        return json_response({"error": {"code": "validation_error", "message": "Передайте аудиофайл."}}, 422)
    return json_response(AssistantTranscriptionResponse(**transcribe_audio(uploaded)).model_dump())
