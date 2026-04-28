from pathlib import Path

import pytest

from app.modules.auth.services import create_user
from app.modules.budget_constructor.models import AnalyticsBudgetFact, AnalyticsSourceFile
from tests.conftest import login, register

TASK_DIR = Path(__file__).resolve().parents[3] / "task"

pytestmark = pytest.mark.skipif(not TASK_DIR.exists(), reason="task data folder is not available")


def test_analytics_sources_and_query(client, app):
    app.config["ANALYTICS_TASK_DIR"] = str(TASK_DIR)
    register(client)

    sources = client.get("/api/v1/analytics/sources")
    assert sources.status_code == 200
    assert sources.get_json()["items"]

    search = client.get("/api/v1/analytics/search?q=6105")
    assert search.status_code == 200
    assert search.get_json()["items"]

    response = client.post(
        "/api/v1/analytics/query",
        json={
            "mode": "template",
            "template_code": "skk",
            "metrics": ["LIMITS", "BO", "AGREEMENT_MBT"],
            "date_mode": "range",
            "date_from": "2025-01-01",
            "date_to": "2026-01-01",
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["rows"]
    assert payload["totals"]["LIMITS"] > 0


def test_analytics_import_demo_requires_admin(client, app):
    app.config["ANALYTICS_TASK_DIR"] = str(TASK_DIR)
    register(client)

    response = client.post("/api/v1/analytics/import-demo", json={"folder_path": str(TASK_DIR)})
    assert response.status_code == 403


def test_analytics_import_demo_persists_dataset_for_admin(client, app):
    app.config["ANALYTICS_TASK_DIR"] = str(TASK_DIR)
    with app.app_context():
        create_user(
            email="admin@example.com",
            username="admin",
            password="password123",
            is_admin=True,
        )

    login(client, email="admin@example.com", password="password123")
    response = client.post("/api/v1/analytics/import-demo")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Демонстрационные данные импортированы в БД."

    with app.app_context():
        assert AnalyticsSourceFile.query.count() == 39
        assert AnalyticsBudgetFact.query.count() > 1000
        assert (
            AnalyticsSourceFile.query.filter_by(source_type="rchb", original_name="март2026.csv").one().rows_imported
            > 0
        )
