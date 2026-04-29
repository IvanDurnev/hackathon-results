import json
from uuid import uuid4
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from cachetools import TTLCache
from ollama import AsyncClient

from app.core.database import get_session
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.ai_request import AiRequestDTO
from app.services.analyse import AnalyticsService
from app.core.config import settings

router = APIRouter(prefix="/ai", tags=["AI chat"])

SESSIONS_HISTORY = TTLCache(maxsize=1000, ttl=7200)

ollama_client = AsyncClient(host=settings.AI_URI)
MODEL = "gemma4:latest"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_budget_report",
            "description": (
                "Получение данных из конструктора бюджетов. "
                "ОБЯЗАТЕЛЬНО period_from и period_to. "
                "ТРЕБУЕТСЯ указать хотя бы один параметр: kcsr_mask ИЛИ budget_name. "
                "Если данных не хватает, переспроси."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "period_from": {
                        "type": "string",
                        "description": "Начало (YYYY-MM)",
                    },
                    "period_to": {"type": "string", "description": "Конец (YYYY-MM)"},
                    "kcsr_mask": {"type": "string", "description": "Маска КЦСР"},
                    "budget_name": {
                        "type": "string",
                        "description": "Наименование бюджета",
                    },
                    "fund_source": {
                        "type": "string",
                        "description": "Источник финансирования",
                    },
                    "min_amount": {
                        "type": "number",
                        "description": "Минимальная сумма",
                    },
                },
                "required": ["period_from", "period_to"],
            },
        },
    }
]


@router.post("/ask")
async def ask_analytics_assistant(
    request: AiRequestDTO, db: AsyncSession = Depends(get_session)
):
    session_id = request.session_id or str(uuid4())
    analytics_service = AnalyticsService(AnalyticsRepository())
    BUDGETS_STR = await analytics_service.get_budget_names(db=db)
    KCSR_STR = await analytics_service.get_kcsrs(db=db)

    SYSTEM_PROMPT = {
        "role": "system",
        "content": (
            "Ты — строго специализированный ИИ-ассистент для работы с финансовой базой данных. "
            "Твоя ЕДИНСТВЕННАЯ цель — вызывать инструмент 'get_budget_report', если запрос пользователя "
            "связан с бюджетами, расходами, лимитами или КЦСР.\n\n"
            f"СПРАВОЧНИК ДОСТУПНЫХ БЮДЖЕТОВ: {', '.join(BUDGETS_STR)}.\n"
            f"СПРАВОЧНИК ДОСТУПНЫХ КЦСР: {', '.join(KCSR_STR)}.\n\n"
            "ПРАВИЛО ИЗВЛЕЧЕНИЯ: При формировании параметров 'budget_name' и 'kcsr_mask' используй "
            "ТОЛЬКО точные значения из справочников выше. Если пользователь написал название с ошибкой "
            "или неформально (например, 'бюджет области'), сопоставь его с наиболее похожим официальным "
            "названием из справочника.\n\n"
            "КРИТИЧЕСКОЕ ПРАВИЛО: Если пользователь задает вопрос на ЛЮБУЮ другую тему (например, "
            "программирование, Python, погода, написание текстов, общие факты), ты СТРОГО ДОЛЖЕН "
            "отказаться отвечать и вернуть текст: 'Я могу помочь только с аналитикой бюджетов.' "
            "Никогда не пиши программный код и не поддерживай диалог на сторонние темы."
        ),
    }
    if session_id in SESSIONS_HISTORY:
        messages = SESSIONS_HISTORY[session_id]
    else:
        messages = [SYSTEM_PROMPT]
        SESSIONS_HISTORY[session_id] = messages

    messages.append({"role": "user", "content": request.query})

    try:
        response1 = await ollama_client.chat(
            model=MODEL, messages=messages, tools=TOOLS
        )

        message1 = response1.get("message", {})
        tool_calls = message1.get("tool_calls")

        if not tool_calls:
            final_text = message1.get("content", "")
            messages.append({"role": "assistant", "content": final_text})
            return {"message": final_text, "session_id": session_id}

        messages.append(message1)

        for tool_call in tool_calls:
            func_name = tool_call["function"]["name"]

            if func_name == "get_budget_report":
                args = tool_call["function"]["arguments"]
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except:
                        args = {}

                kcsr = args.get("kcsr_mask", "")
                b_name = args.get("budget_name", "")

                if not kcsr and not b_name:
                    raise HTTPException(
                        status_code=400, detail="Требуется kcsr_mask или budget_name."
                    )

                try:
                    p_from = str(args.get("period_from", ""))[:7]
                    p_to = str(args.get("period_to", ""))[:7]

                    min_amt = Decimal(str(args.get("min_amount", 0)))

                    raw_data = await analytics_service.get_constructor_report(
                        db=db,
                        kcsr_mask=kcsr,
                        budget_name=b_name,
                        period_from=p_from,
                        period_to=p_to,
                        fund_source=args.get("fund_source"),
                        min_amount=min_amt,
                    )

                    return raw_data

                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))

        raise HTTPException(status_code=400, detail="Неизвестная функция.")

    except HTTPException:
        raise
    except Exception as e:
        SESSIONS_HISTORY.pop(session_id, None)
        raise HTTPException(status_code=500, detail=str(e))
