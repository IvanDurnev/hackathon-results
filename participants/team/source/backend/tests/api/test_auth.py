from app import create_app
from app.extensions import db
from app.modules.auth.models import User
from app.modules.auth.services import create_user
from tests.conftest import login, register


def test_register_login_logout(client, app):
    response = register(client)
    assert response.status_code == 201

    with app.app_context():
        user = User.query.filter_by(email="user@example.com").first()
        assert user is not None
        assert user.password_hash != "password123"
        assert user.has_role("user")

    assert client.get("/api/v1/auth/me").status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert login(client).status_code == 200


def test_login_accepts_username(client, app):
    register(client)
    client.post("/api/v1/auth/logout")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json["user"]["username"] == "user"


def test_register_rejects_blank_display_name(client):
    response = register(client, display_name="   ")

    assert response.status_code == 422
    assert response.json["error"]["code"] == "validation_error"


def test_session_survives_user_agent_change(client):
    register(client)

    response = client.get(
        "/api/v1/auth/me",
        headers={"User-Agent": "Mozilla/5.0 Desktop"},
    )
    assert response.status_code == 200

    response = client.get(
        "/api/v1/auth/me",
        headers={"User-Agent": "Mozilla/5.0 Mobile DevTools"},
    )
    assert response.status_code == 200


def test_inactive_user_cannot_login(client, app):
    with app.app_context():
        create_user("inactive@example.com", "inactive", "password123", active=False)
        db.session.commit()

    response = login(client, "inactive@example.com", "password123")
    assert response.status_code == 403


def test_login_preflight_allows_loopback_frontend_origin(client):
    app = create_app(
        "development",
        {
            "SERVER_NAME": "localhost",
        },
    )
    test_client = app.test_client()

    response = test_client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == "http://127.0.0.1:5173"
    assert response.headers.get("Access-Control-Allow-Credentials") == "true"
