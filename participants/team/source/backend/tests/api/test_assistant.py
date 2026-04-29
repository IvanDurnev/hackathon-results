from app.modules.auth.services import create_user
from app.modules.assistant import services as assistant_services
from tests.conftest import login


def test_assistant_chat_uses_backend_proxy(client, app, monkeypatch):
    with app.app_context():
        create_user("assistant@example.com", "assistant", "password123")

    login(client, "assistant@example.com", "password123")

    def fake_ask_assistant(*, prompt, messages, context):
        assert prompt == "Подбери параметры СКК"
        assert context["rows"] == 0
        return {"text": "Используйте шаблон СКК.", "provider": "local", "model": "test"}

    monkeypatch.setattr("app.modules.assistant.routes.ask_assistant", fake_ask_assistant)

    response = client.post(
        "/api/v1/assistant/chat",
        json={"prompt": "Подбери параметры СКК", "context": {"rows": 0}},
    )

    assert response.status_code == 200
    assert response.get_json()["text"] == "Используйте шаблон СКК."


def test_assistant_service_executes_tool_call(monkeypatch):
    responses = [
        {
            "text": "",
            "provider": "local",
            "model": "test",
            "tool_calls": [
                {
                    "id": "call-1",
                    "function": {
                        "name": "run_analytics_query",
                        "arguments": {
                            "mode": "template",
                            "template_code": "skk",
                            "metrics": ["LIMITS"],
                            "date_mode": "range",
                            "date_from": "2025-01-01",
                            "date_to": "2026-04-01",
                        },
                    },
                }
            ],
        },
        {"text": "Активная выборка обновлена.", "provider": "local", "model": "test"},
    ]

    def fake_post_chat(payload):
        assert payload["messages"]
        return responses.pop(0)

    def fake_execute_tool_call(call, context):
        assert call["name"] == "run_analytics_query"
        return {
            "summary": "Активная выборка обновлена: шаблон skk.",
            "action": {
                "type": "apply_analytics_selection",
                "label": "Активная выборка обновлена: шаблон skk.",
                "payload": call["arguments"],
            },
        }

    monkeypatch.setattr(assistant_services, "_post_chat", fake_post_chat)
    monkeypatch.setattr(assistant_services, "_execute_tool_call", fake_execute_tool_call)

    response = assistant_services.ask_assistant(prompt="Покажи СКК", messages=[], context={})

    assert response["text"] == "Активная выборка обновлена."
    assert response["tool_calls"][0]["name"] == "run_analytics_query"
    assert response["actions"][0]["type"] == "apply_analytics_selection"


def test_assistant_service_executes_textual_tool_code(monkeypatch):
    responses = [
        {
            "text": '```tool_code\nrun_analytics_query(selection="skk", period="2025", indicators=["BO", "REST_LIMITS"])\n```',
            "provider": "local",
            "model": "test",
        },
        {"text": "Активная выборка обновлена.", "provider": "local", "model": "test"},
    ]

    def fake_post_chat(payload):
        return responses.pop(0)

    def fake_execute_tool_call(call, context):
        assert call["arguments"]["template_code"] == "skk"
        assert call["arguments"]["date_from"] == "2025-01-01"
        assert call["arguments"]["date_to"] == "2026-01-01"
        assert call["arguments"]["metrics"] == ["BO", "REST_LIMITS"]
        return {
            "summary": "Активная выборка обновлена: шаблон skk.",
            "action": {
                "type": "apply_analytics_selection",
                "label": "Активная выборка обновлена: шаблон skk.",
                "payload": call["arguments"],
            },
        }

    monkeypatch.setattr(assistant_services, "_post_chat", fake_post_chat)
    monkeypatch.setattr(assistant_services, "_execute_tool_call", fake_execute_tool_call)

    response = assistant_services.ask_assistant(prompt="СКК за 2025г", messages=[], context={})

    assert response["text"] == "Активная выборка обновлена."
    assert response["tool_calls"][0]["name"] == "run_analytics_query"
    assert response["actions"][0]["type"] == "apply_analytics_selection"
