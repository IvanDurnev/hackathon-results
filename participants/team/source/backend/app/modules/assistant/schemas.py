from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AssistantMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)


class AssistantChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    messages: list[AssistantMessage] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)


class AssistantChatResponse(BaseModel):
    text: str
    provider: str | None = None
    model: str | None = None
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    actions: list[dict[str, Any]] = Field(default_factory=list)


class AssistantHealthResponse(BaseModel):
    ok: bool
    providers: list[str] = Field(default_factory=list)
    message: str | None = None


class AssistantTranscriptionResponse(BaseModel):
    text: str
