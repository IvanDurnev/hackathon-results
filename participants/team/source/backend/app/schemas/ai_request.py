from pydantic import BaseModel


class AiRequestDTO(BaseModel):
    query: str
    session_id: str | None = None
