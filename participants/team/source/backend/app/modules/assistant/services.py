from __future__ import annotations

import json
import re
from typing import Any

import requests
from flask import current_app
from werkzeug.datastructures import FileStorage

from app.core.errors import AppError, ValidationAppError
from app.modules.budget_constructor.schemas import AnalyticsQueryRequest
from app.modules.budget_constructor.services import (
    build_compare,
    build_query_result,
    find_objects,
    get_dataset,
    list_metrics,
    list_templates,
)


SYSTEM_PROMPT = """Ты ИИ-помощник конструктора аналитических выборок.
Отвечай по-русски, кратко и прикладно. Если пользователь просит подобрать параметры выборки,
предложи режим, шаблон, период и показатели.

Для вопросов по бюджетным данным используй инструменты. Не выдумывай строки, суммы, объекты,
коды и периоды. Если пользователь просит показать, сформировать, найти или объяснить выборку,
сначала найди объект или сформируй выборку инструментом, затем кратко объясни результат.
Если инструмент run_analytics_query успешно сформировал выборку, явно напиши:
"Активная выборка обновлена" и перечисли ключевые параметры."""


class AssistantUnavailable(AppError):
    status_code = 503
    code = "assistant_unavailable"
    message = "ИИ-модуль недоступен."


def assistant_health() -> dict[str, Any]:
    try:
        response = _session().get(_module_url("/health"), headers=_headers(), timeout=_timeout())
    except requests.RequestException as exc:
        return {"ok": False, "providers": [], "message": str(exc)}

    if response.status_code >= 400:
        return {"ok": False, "providers": [], "message": _error_message(response)}
    payload = _json(response)
    return {
        "ok": bool(payload.get("ok")),
        "providers": payload.get("providers") if isinstance(payload.get("providers"), list) else [],
        "message": payload.get("error") if isinstance(payload.get("error"), str) else None,
    }


def ask_assistant(*, prompt: str, messages: list[dict[str, str]], context: dict[str, Any]) -> dict[str, Any]:
    prepared_messages = _build_messages(prompt=prompt, messages=messages, context=context)
    tool_events: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    fallback_used = False

    for _ in range(3):
        payload = _chat_payload(prepared_messages, tools=_assistant_tools())
        try:
            module_payload = _post_chat(payload)
        except AssistantUnavailable:
            if actions:
                return _tool_only_response(tool_events=tool_events, actions=actions)
            raise
        tool_calls = _normalize_tool_calls(module_payload.get("tool_calls"))
        if not tool_calls:
            text = module_payload.get("text")
            if not isinstance(text, str) or not text.strip():
                raise AssistantUnavailable("ИИ-модуль вернул пустой ответ.")
            if not fallback_used and not tool_events:
                fallback_calls = _fallback_tool_calls(text=text, prompt=prompt)
                if fallback_calls:
                    fallback_used = True
                    tool_calls = fallback_calls
                    prepared_messages.append(_assistant_tool_call_message({"text": text}, tool_calls))
                    for call in tool_calls:
                        result = _execute_tool_call(call, context)
                        tool_events.append(
                            {
                                "name": call["name"],
                                "arguments": call["arguments"],
                                "status": "error" if result.get("error") else "completed",
                                "summary": result.get("summary") or result.get("error"),
                            }
                        )
                        action = result.get("action")
                        if isinstance(action, dict):
                            actions.append(action)
                        prepared_messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call["id"],
                                "name": call["name"],
                                "content": json.dumps(result, ensure_ascii=False),
                            }
                        )
                    continue
            return {
                "text": text.strip(),
                "provider": module_payload.get("provider"),
                "model": module_payload.get("model"),
                "tool_calls": tool_events,
                "actions": actions,
            }

        prepared_messages.append(_assistant_tool_call_message(module_payload, tool_calls))
        for call in tool_calls:
            result = _execute_tool_call(call, context)
            tool_events.append(
                {
                    "name": call["name"],
                    "arguments": call["arguments"],
                    "status": "error" if result.get("error") else "completed",
                    "summary": result.get("summary") or result.get("error"),
                }
            )
            action = result.get("action")
            if isinstance(action, dict):
                actions.append(action)
            prepared_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "name": call["name"],
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    try:
        module_payload = _post_chat(_chat_payload(prepared_messages, tools=[]))
    except AssistantUnavailable:
        if actions:
            return _tool_only_response(tool_events=tool_events, actions=actions)
        raise
    text = module_payload.get("text")
    if not isinstance(text, str) or not text.strip():
        text = "Инструменты выполнены, но модель не вернула текстовый ответ."
    return {
        "text": text.strip(),
        "provider": module_payload.get("provider"),
        "model": module_payload.get("model"),
        "tool_calls": tool_events,
        "actions": actions,
    }


def _tool_only_response(*, tool_events: list[dict[str, Any]], actions: list[dict[str, Any]]) -> dict[str, Any]:
    label = next(
        (str(action.get("label")) for action in actions if isinstance(action.get("label"), str)),
        "Инструмент выполнен.",
    )
    return {
        "text": label,
        "provider": None,
        "model": None,
        "tool_calls": tool_events,
        "actions": actions,
    }


def _post_chat(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        response = _session().post(_module_url("/chat"), headers=_headers(), json=payload, timeout=_timeout())
    except requests.RequestException as exc:
        raise AssistantUnavailable(str(exc)) from exc

    if response.status_code >= 400:
        raise AssistantUnavailable(_error_message(response))

    return _json(response)


def _chat_payload(messages: list[dict[str, Any]], *, tools: list[dict[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 900,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    return payload


def _assistant_tools() -> list[dict[str, Any]]:
    metric_codes = [metric["code"] for metric in list_metrics()]
    template_codes = [template["code"] for template in list_templates()]
    return [
        {
            "type": "function",
            "function": {
                "name": "get_analytics_reference",
                "description": "Вернуть доступные шаблоны, показатели, источники и примеры объектов.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_analytics_objects",
                "description": "Найти объекты в импортированных бюджетных данных по названию или коду.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Название, фрагмент названия или код объекта."},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 10},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_analytics_query",
                "description": (
                    "Сформировать реальную аналитическую выборку по БД. Используй этот инструмент, "
                    "когда пользователь просит показать, сформировать, посчитать или обновить выборку."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mode": {"type": "string", "enum": ["search", "template"], "default": "search"},
                        "template_code": {"type": "string", "enum": template_codes},
                        "query": {"type": "string"},
                        "object_keys": {"type": "array", "items": {"type": "string"}, "default": []},
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string", "enum": metric_codes},
                            "minItems": 1,
                            "description": "Коды показателей из справочника.",
                        },
                        "date_mode": {"type": "string", "enum": ["range", "compare"], "default": "range"},
                        "date_from": {"type": "string", "description": "YYYY-MM-DD для режима range."},
                        "date_to": {"type": "string", "description": "YYYY-MM-DD для режима range."},
                        "base_date": {"type": "string", "description": "YYYY-MM-DD для режима compare."},
                        "compare_date": {"type": "string", "description": "YYYY-MM-DD для режима compare."},
                    },
                    "required": ["mode", "metrics", "date_mode"],
                    "additionalProperties": False,
                },
            },
        },
    ]


def _normalize_tool_calls(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    calls: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        function = item.get("function")
        if not isinstance(function, dict):
            continue
        name = function.get("name")
        arguments = function.get("arguments")
        if not isinstance(name, str) or not name:
            continue
        calls.append(
            {
                "id": str(item.get("id") or name),
                "name": name,
                "arguments": arguments if isinstance(arguments, dict) else {},
            }
        )
    return calls


def _fallback_tool_calls(*, text: str, prompt: str) -> list[dict[str, Any]]:
    arguments = _arguments_from_tool_code(text)
    if arguments is None:
        arguments = _infer_query_arguments(f"{prompt}\n{text}")
    if not arguments:
        return []
    return [
        {
            "id": "fallback-run-analytics-query",
            "name": "run_analytics_query",
            "arguments": arguments,
        }
    ]


def _arguments_from_tool_code(text: str) -> dict[str, Any] | None:
    match = re.search(r"run_analytics_query\s*\((?P<body>.*?)\)", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None

    parsed: dict[str, Any] = {}
    for key, value in re.findall(r"(\w+)\s*=\s*(\[[^\]]*\]|\"[^\"]*\"|'[^']*'|[^\s,]+)", match.group("body")):
        parsed[key] = _parse_pseudo_value(value)
    return _normalize_llm_query_payload(parsed)


def _parse_pseudo_value(value: str) -> Any:
    raw = value.strip().rstrip(",")
    if raw.startswith("[") and raw.endswith("]"):
        try:
            parsed = json.loads(raw.replace("'", '"'))
        except json.JSONDecodeError:
            return [item.strip().strip("\"'") for item in raw.strip("[]").split(",") if item.strip()]
        return parsed
    return raw.strip("\"'")


def _infer_query_arguments(text: str) -> dict[str, Any] | None:
    lowered = text.lower()
    template_code = None
    if "скк" in lowered or "6105" in lowered:
        template_code = "skk"
    elif "кик" in lowered or "978" in lowered:
        template_code = "kik"
    elif "окв" in lowered:
        template_code = "okv"
    elif "2/3" in lowered or "970" in lowered:
        template_code = "two_three"

    year_match = re.search(r"\b(20\d{2})\s*(?:г|год)?\b", lowered)
    metrics = _metrics_from_text(text)
    if not template_code and not metrics:
        return None

    payload: dict[str, Any] = {
        "mode": "template" if template_code else "search",
        "template_code": template_code,
        "metrics": metrics or ["LIMITS", "BO", "BO_FREE", "REST_LIMITS", "CASH_RCHB"],
        "date_mode": "range",
        "object_keys": [],
    }
    if year_match:
        year = int(year_match.group(1))
        payload["date_from"] = f"{year}-01-01"
        payload["date_to"] = f"{year + 1}-01-01"
    return _normalize_llm_query_payload(payload)


def _normalize_llm_query_payload(value: dict[str, Any]) -> dict[str, Any]:
    selection = value.get("selection") or value.get("template") or value.get("template_code")
    metrics = value.get("metrics") or value.get("indicators") or value.get("indicator_codes")
    period = value.get("period") or value.get("year")

    payload: dict[str, Any] = {
        "mode": value.get("mode") or ("template" if selection else "search"),
        "template_code": _normalize_template_code(selection),
        "query": value.get("query"),
        "object_keys": value.get("object_keys") if isinstance(value.get("object_keys"), list) else [],
        "metrics": _normalize_metric_codes(metrics),
        "date_mode": value.get("date_mode") or "range",
        "date_from": value.get("date_from"),
        "date_to": value.get("date_to"),
        "base_date": value.get("base_date"),
        "compare_date": value.get("compare_date"),
    }

    if period and not payload["date_from"] and not payload["date_to"]:
        year_match = re.search(r"(20\d{2})", str(period))
        if year_match:
            year = int(year_match.group(1))
            payload["date_from"] = f"{year}-01-01"
            payload["date_to"] = f"{year + 1}-01-01"

    if payload["template_code"]:
        payload["mode"] = "template"
    if not payload["metrics"]:
        payload["metrics"] = ["LIMITS", "BO", "BO_FREE", "REST_LIMITS", "CASH_RCHB"]
    return payload


def _normalize_template_code(value: Any) -> str | None:
    text = str(value or "").strip().lower()
    aliases = {
        "kik": "kik",
        "кик": "kik",
        "skk": "skk",
        "скк": "skk",
        "two_three": "two_three",
        "2/3": "two_three",
        "okv": "okv",
        "окв": "okv",
    }
    return aliases.get(text)


def _normalize_metric_codes(value: Any) -> list[str]:
    if isinstance(value, str):
        raw_items = [value]
    elif isinstance(value, list):
        raw_items = [str(item) for item in value]
    else:
        return []

    available = {metric["code"] for metric in list_metrics()}
    result: list[str] = []
    for item in raw_items:
        code = item.strip().upper()
        if code in available and code not in result:
            result.append(code)
    return result


def _metrics_from_text(text: str) -> list[str]:
    available = {metric["code"] for metric in list_metrics()}
    result: list[str] = []
    upper = text.upper()
    for code in available:
        if re.search(rf"\b{re.escape(code)}\b", upper) and code not in result:
            result.append(code)

    lowered = text.lower()
    keyword_metrics = [
        ("без бо", "BO_FREE"),
        ("остат", "REST_LIMITS"),
        ("касс", "CASH_RCHB"),
        ("лимит", "LIMITS"),
        ("бо", "BO"),
        ("обязатель", "BO"),
        ("договор", "CONTRACT_AMOUNT"),
        ("контракт", "CONTRACT_AMOUNT"),
        ("плат", "CONTRACT_PAYMENT"),
        ("соглаш", "AGREEMENT_MBT"),
    ]
    for keyword, code in keyword_metrics:
        if keyword in lowered and code not in result:
            result.append(code)
    return result


def _assistant_tool_call_message(module_payload: dict[str, Any], tool_calls: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": module_payload.get("text") if isinstance(module_payload.get("text"), str) else "",
        "tool_calls": [
            {
                "id": call["id"],
                "type": "function",
                "function": {
                    "name": call["name"],
                    "arguments": json.dumps(call["arguments"], ensure_ascii=False),
                },
            }
            for call in tool_calls
        ],
    }


def _execute_tool_call(call: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    name = call["name"]
    arguments = call["arguments"]
    try:
        if name == "get_analytics_reference":
            return _analytics_reference(context)
        if name == "search_analytics_objects":
            return _tool_search_objects(arguments)
        if name == "run_analytics_query":
            return _tool_run_query(arguments)
        return {"error": f"Неизвестный инструмент: {name}"}
    except Exception as exc:  # noqa: BLE001 - tool errors are returned to the model.
        return {"error": str(exc), "summary": f"Инструмент {name} завершился ошибкой."}


def _analytics_reference(context: dict[str, Any]) -> dict[str, Any]:
    dataset = get_dataset()
    sources = sorted(
        dataset.source_files,
        key=lambda source: (source.source_type, source.period_date.isoformat() if source.period_date else ""),
    )
    return {
        "summary": "Справочник аналитики получен.",
        "metrics": list_metrics(),
        "templates": list_templates(),
        "current_context": context,
        "sources": [
            {
                "source_type": source.source_type,
                "file": source.original_name,
                "period_date": source.period_date.isoformat() if source.period_date else None,
                "rows_imported": source.rows_imported,
                "errors": source.errors_count,
            }
            for source in sources[-25:]
        ],
        "object_examples": _object_examples(dataset),
    }


def _tool_search_objects(arguments: dict[str, Any]) -> dict[str, Any]:
    query = str(arguments.get("query") or "").strip()
    if len(query) < 2:
        return {"error": "Для поиска объекта нужна строка минимум из 2 символов."}
    limit = _bounded_int(arguments.get("limit"), default=10, minimum=1, maximum=20)
    hits = find_objects(query)[:limit]
    return {
        "summary": f"Найдено объектов: {len(hits)}.",
        "items": [
            {
                "object_key": hit.object_key,
                "display_name": hit.display_name,
                "object_type": hit.object_type,
                "matched_codes": hit.matched_codes,
                "source_types": hit.source_types,
            }
            for hit in hits
        ],
    }


def _tool_run_query(arguments: dict[str, Any]) -> dict[str, Any]:
    payload_dict = _normalize_query_arguments(arguments)
    payload = AnalyticsQueryRequest.model_validate(payload_dict)
    if payload.date_mode == "compare":
        result = build_compare(payload)
        rows = result.rows
        return {
            "summary": _selection_summary(payload, len(rows), sum(float(row.compare_value) for row in rows)),
            "rows_count": len(rows),
            "preview_rows": [
                {
                    "object_name": row.object_name,
                    "metric": row.metric_name,
                    "base_value": float(row.base_value),
                    "compare_value": float(row.compare_value),
                    "delta": float(row.delta),
                }
                for row in rows[:10]
            ],
            "action": _apply_selection_action(payload, len(rows)),
        }

    result = build_query_result(payload)
    total_amount = sum(float(value) for value in result.totals.values())
    return {
        "summary": _selection_summary(payload, len(result.rows), total_amount),
        "rows_count": len(result.rows),
        "totals": {key: float(value) for key, value in result.totals.items()},
        "warnings_count": len(result.warnings),
        "preview_rows": [
            {
                "object_name": row.object_name,
                "metric": row.metric_name,
                "amount": float(row.amount),
                "source_type": row.source_type,
                "codes": row.codes,
            }
            for row in result.rows[:10]
        ],
        "action": _apply_selection_action(payload, len(result.rows)),
    }


def _normalize_query_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    payload = dict(arguments)
    payload.setdefault("mode", "template" if payload.get("template_code") else "search")
    payload.setdefault("object_keys", [])
    payload.setdefault("date_mode", "range")
    if not payload.get("metrics"):
        payload["metrics"] = ["LIMITS", "BO", "CASH_RCHB"]
    if payload.get("mode") == "template" and not payload.get("template_code"):
        payload["mode"] = "search"
    if payload.get("mode") == "search":
        payload["template_code"] = None
    return payload


def _apply_selection_action(payload: AnalyticsQueryRequest, rows_count: int) -> dict[str, Any]:
    payload_json = payload.model_dump(mode="json")
    return {
        "type": "apply_analytics_selection",
        "label": f"Активная выборка обновлена: {_payload_label(payload)}; строк: {rows_count}.",
        "payload": payload_json,
    }


def _selection_summary(payload: AnalyticsQueryRequest, rows_count: int, amount: float) -> str:
    return f"Активная выборка обновлена: {_payload_label(payload)}; строк: {rows_count}; сумма: {amount:,.2f}."


def _payload_label(payload: AnalyticsQueryRequest) -> str:
    if payload.mode == "template" and payload.template_code:
        base = f"шаблон {payload.template_code}"
    elif payload.query:
        base = f"поиск '{payload.query}'"
    elif payload.object_keys:
        base = f"объекты {len(payload.object_keys)}"
    else:
        base = "выборка"
    if payload.date_mode == "compare":
        return f"{base}, сравнение {payload.base_date} -> {payload.compare_date}"
    return f"{base}, период {payload.date_from or 'начало'} -> {payload.date_to or 'конец'}"


def _object_examples(dataset) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    seen: set[str] = set()
    for fact in dataset.budget_facts:
        if not fact.kcsr_norm or not fact.kcsr_name:
            continue
        key = f"kcsr:{fact.kcsr_norm}"
        if key in seen:
            continue
        seen.add(key)
        examples.append(
            {
                "object_key": key,
                "display_name": fact.kcsr_name,
                "kcsr": fact.kcsr_norm,
                "source_type": fact.source_type,
            }
        )
        if len(examples) >= 25:
            break
    return examples


def _bounded_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return min(max(number, minimum), maximum)


def transcribe_audio(file: FileStorage) -> dict[str, str]:
    if not file.filename:
        raise ValidationAppError("Передайте аудиофайл для распознавания.")

    files = {
        "file": (
            file.filename,
            file.stream,
            file.mimetype or "application/octet-stream",
        )
    }
    data = _transcription_options()
    try:
        response = _session().post(
            _module_url("/transcribe"),
            headers=_headers(),
            files=files,
            data=data,
            timeout=max(_timeout(), 120),
        )
    except requests.RequestException as exc:
        raise AssistantUnavailable(str(exc)) from exc

    if response.status_code >= 400:
        raise AssistantUnavailable(_error_message(response))

    payload = _json(response)
    text = payload.get("text")
    if not isinstance(text, str):
        raise AssistantUnavailable("ИИ-модуль не вернул текст распознавания.")
    return {"text": text}


def _transcription_options() -> dict[str, str]:
    data: dict[str, str] = {}
    model = current_app.config.get("AI_MODULE_STT_MODEL")
    language = current_app.config.get("AI_MODULE_STT_LANGUAGE")
    if model:
        data["model"] = str(model)
    if language:
        data["language"] = str(language)
    return data


def _build_messages(*, prompt: str, messages: list[dict[str, str]], context: dict[str, Any]) -> list[dict[str, str]]:
    prepared = [{"role": "system", "content": SYSTEM_PROMPT}]
    context_text = _context_to_text(context)
    if context_text:
        prepared.append({"role": "system", "content": context_text})

    for message in messages[-10:]:
        role = message.get("role")
        content = message.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            prepared.append({"role": role, "content": content.strip()})
    prepared.append({"role": "user", "content": prompt})
    return prepared


def _context_to_text(context: dict[str, Any]) -> str:
    if not context:
        context = {}
    lines = ["Текущий контекст интерфейса:"]
    for key in ("selection", "rows", "amount", "warnings"):
        value = context.get(key)
        if value not in (None, ""):
            lines.append(f"- {key}: {value}")
    metrics = context.get("metrics")
    if isinstance(metrics, list) and metrics:
        lines.append(f"- metrics: {', '.join(str(item) for item in metrics[:12])}")
    available_metrics = context.get("available_metrics")
    if isinstance(available_metrics, list) and available_metrics:
        lines.append("- Доступные показатели:")
        for item in available_metrics[:20]:
            if isinstance(item, dict):
                lines.append(f"  - {item.get('code')}: {item.get('name')}")
    else:
        lines.append("- Доступные показатели:")
        for metric in list_metrics():
            lines.append(f"  - {metric['code']}: {metric['name']}")

    templates = context.get("templates")
    if not isinstance(templates, list) or not templates:
        templates = list_templates()
    lines.append("- Контрольные шаблоны:")
    for template in templates[:12]:
        if isinstance(template, dict):
            lines.append(f"  - {template.get('code')}: {template.get('name')} ({template.get('description')})")

    objects = context.get("objects")
    if isinstance(objects, list) and objects:
        lines.append("- Выбранные/найденные объекты в интерфейсе:")
        for item in objects[:10]:
            if isinstance(item, dict):
                lines.append(f"  - {item.get('object_key')}: {item.get('display_name')}")
    lines.append("Если нужен другой объект, используй search_analytics_objects.")
    return "\n".join(lines)


def _module_url(path: str) -> str:
    base_url = str(current_app.config.get("AI_MODULE_URL") or "").rstrip("/")
    if not base_url:
        raise AssistantUnavailable("AI_MODULE_URL не настроен.")
    return f"{base_url}{path}"


def _headers() -> dict[str, str]:
    api_key = current_app.config.get("AI_MODULE_API_KEY")
    return {"X-AI-Module-Key": str(api_key)} if api_key else {}


def _timeout() -> float:
    return float(current_app.config.get("AI_MODULE_TIMEOUT_SECONDS", 60))


def _session() -> requests.Session:
    return requests.Session()


def _json(response: requests.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _error_message(response: requests.Response) -> str:
    payload = _json(response)
    error = payload.get("error")
    if isinstance(error, dict) and isinstance(error.get("message"), str):
        return error["message"]
    if isinstance(error, str):
        return error
    if isinstance(payload.get("message"), str):
        return payload["message"]
    return response.text[:300] or "ИИ-модуль вернул ошибку."
