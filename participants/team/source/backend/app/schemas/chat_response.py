from pydantic import BaseModel

from app.schemas.analytics import BudgetAnalyticsDTO


class ChatResponseDTO(BaseModel):
    response: list[BudgetAnalyticsDTO]
    session_id: str
