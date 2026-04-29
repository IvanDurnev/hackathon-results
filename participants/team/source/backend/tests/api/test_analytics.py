from contextlib import ExitStack
from pathlib import Path

import pytest

from app.modules.auth.services import create_user
from app.modules.budget_constructor.models import AnalyticsBudgetFact, AnalyticsSourceFile
from tests.conftest import login, register

TASK_DIR = Path(__file__).resolve().parents[3] / "task"

pytestmark = pytest.mark.skipif(not TASK_DIR.exists(), reason="task data folder is not available")


def test_analytics_sources_and_query(client, app):
    app.config["ANALYTICS_TASK_DIR"] = str(TASK_DIR)
    with app.app_context():
        create_user(
            email="admin-query@example.com",
            username="admin-query",
            password="password123",
            is_admin=True,
        )

    login(client, email="admin-query@example.com", password="password123")
    imported = client.post("/api/v1/analytics/import")
    assert imported.status_code == 200

    client.post("/api/v1/auth/logout")
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

    compare_response = client.post(
        "/api/v1/analytics/compare",
        json={
            "mode": "template",
            "template_code": "skk",
            "metrics": ["LIMITS", "BO", "CASH_RCHB"],
            "date_mode": "compare",
            "base_date": "2025-02-01",
            "compare_date": "2026-01-01",
        },
    )
    assert compare_response.status_code == 200
    assert compare_response.get_json()["items"]

    search_response = client.post(
        "/api/v1/analytics/query",
        json={
            "mode": "search",
            "query": "6105",
            "object_keys": [],
            "metrics": ["LIMITS", "BO", "AGREEMENT_MBT"],
            "date_mode": "range",
            "date_from": "2025-01-01",
            "date_to": "2026-04-01",
        },
    )
    assert search_response.status_code == 200
    assert search_response.get_json()["rows"]


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
    response = client.post("/api/v1/analytics/import")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Данные импортированы в БД."

    with app.app_context():
        assert AnalyticsSourceFile.query.count() == 39
        assert AnalyticsBudgetFact.query.count() > 1000
        assert (
            AnalyticsSourceFile.query.filter_by(source_type="rchb", original_name="март2026.csv").one().rows_imported
            > 0
        )

    delete_response = client.delete("/api/v1/analytics/import")
    assert delete_response.status_code == 200
    assert delete_response.get_json()["message"] == "Импортированные данные удалены из БД."

    with app.app_context():
        assert AnalyticsSourceFile.query.count() == 0
        assert AnalyticsBudgetFact.query.count() == 0


def test_analytics_import_accepts_uploaded_folder(client, app):
    with app.app_context():
        create_user(
            email="admin-upload@example.com",
            username="admin-upload",
            password="password123",
            is_admin=True,
        )

    login(client, email="admin-upload@example.com", password="password123")

    with ExitStack() as stack:
        files = [
            (stack.enter_context(path.open("rb")), str(path.relative_to(TASK_DIR.parent)))
            for path in TASK_DIR.rglob("*")
            if path.is_file()
        ]
        response = client.post(
            "/api/v1/analytics/import",
            data={"files": files},
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Данные импортированы в БД."

    with app.app_context():
        assert AnalyticsSourceFile.query.count() == 39
        assert AnalyticsBudgetFact.query.count() > 1000
