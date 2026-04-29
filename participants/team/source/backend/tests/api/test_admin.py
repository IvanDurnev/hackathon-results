from app.extensions import db
from app.modules.auth.models import User
from app.modules.auth.services import create_user, ensure_default_roles
from tests.conftest import login


def test_admin_can_list_users(client, app):
    with app.app_context():
        admin = create_user("admin-list@example.com", "admin-list", "password123", is_admin=True)
        create_user("regular@example.com", "regular", "password123")
        admin_email = admin.email

    login(client, admin_email, "password123")
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 200
    assert response.json["pagination"]["total"] == 2
    assert set(response.json["items"][0].keys()) >= {"id", "email", "username", "roles", "active"}


def test_admin_can_search_users_by_role_label(client, app):
    with app.app_context():
        admin = create_user("admin-search@example.com", "admin-search", "password123", is_admin=True)
        create_user("admin-search-2@example.com", "admin-search-2", "password123", is_admin=True)
        create_user("regular-search@example.com", "regular-search", "password123")
        admin_email = admin.email

    login(client, admin_email, "password123")
    response = client.get("/api/v1/admin/users", query_string={"q": "Админ"})

    assert response.status_code == 200
    assert response.json["pagination"]["total"] == 2
    assert all("admin" in item["roles"] for item in response.json["items"])


def test_admin_user_list_tolerates_dirty_email_data(client, app):
    with app.app_context():
        admin = create_user("dirty-admin@example.com", "dirty-admin", "password123", is_admin=True)
        roles = ensure_default_roles()
        dirty = User(
            email=".\\.venv\\scripts\\python.exe -m flask --app wsgi run --debug",
            username="dirty",
            active=True,
        )
        dirty.set_password("password123")
        dirty.add_role(roles["user"])
        db.session.add(dirty)
        db.session.commit()
        admin_email = admin.email

    login(client, admin_email, "password123")
    response = client.get("/api/v1/admin/users")

    assert response.status_code == 200
    assert response.json["pagination"]["total"] == 2


def test_admin_cannot_deactivate_self(client, app):
    with app.app_context():
        admin = create_user("admin-self@example.com", "admin-self", "password123", is_admin=True)
        admin_id = admin.id
        admin_email = admin.email

    login(client, admin_email, "password123")
    response = client.patch(f"/api/v1/admin/users/{admin_id}", json={"active": False})
    assert response.status_code == 403


def test_admin_can_create_update_and_delete_user(client, app):
    with app.app_context():
        admin = create_user("admin-manage@example.com", "admin-manage", "password123", is_admin=True)
        admin_email = admin.email

    login(client, admin_email, "password123")

    response = client.post(
        "/api/v1/admin/users",
        json={
            "email": "created@example.com",
            "username": "created-user",
            "display_name": "Created User",
            "password": "password123",
            "active": True,
            "is_admin": False,
        },
    )
    assert response.status_code == 201
    user_id = response.json["user"]["id"]

    response = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={
            "email": "updated@example.com",
            "username": "updated-user",
            "display_name": "Updated User",
            "is_admin": True,
            "active": False,
            "password": "new-password123",
        },
    )
    assert response.status_code == 200
    assert response.json["user"]["email"] == "updated@example.com"
    assert "admin" in response.json["user"]["roles"]
    assert response.json["user"]["active"] is False

    response = client.delete(f"/api/v1/admin/users/{user_id}")
    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(User, user_id) is None


def test_admin_create_user_rejects_blank_display_name(client, app):
    with app.app_context():
        admin = create_user("admin-validation@example.com", "admin-validation", "password123", is_admin=True)
        admin_email = admin.email

    login(client, admin_email, "password123")
    response = client.post(
        "/api/v1/admin/users",
        json={
            "email": "invalid@example.com",
            "username": "invalid-user",
            "display_name": "   ",
            "password": "password123",
            "active": True,
            "is_admin": False,
        },
    )

    assert response.status_code == 422
    assert response.json["error"]["code"] == "validation_error"


def test_admin_cannot_delete_self(client, app):
    with app.app_context():
        admin = create_user("delete-self@example.com", "delete-self", "password123", is_admin=True)
        admin_id = admin.id
        admin_email = admin.email

    login(client, admin_email, "password123")
    response = client.delete(f"/api/v1/admin/users/{admin_id}")

    assert response.status_code == 403
