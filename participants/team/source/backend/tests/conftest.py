from pathlib import Path
import shutil

import pytest

from app import create_app
from app.extensions import db
from app.modules.auth.services import ensure_default_roles


@pytest.fixture()
def app():
    upload_dir = Path(__file__).resolve().parents[1] / "instance" / "test-uploads"
    app = create_app(
        "testing",
        {
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SERVER_NAME": "localhost",
            "UPLOAD_FOLDER": str(upload_dir),
        },
    )

    with app.app_context():
        db.create_all()
        ensure_default_roles()
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()
    shutil.rmtree(upload_dir, ignore_errors=True)


@pytest.fixture()
def client(app):
    return app.test_client()


def register(
    client,
    email="user@example.com",
    username="user",
    password="password123",
    display_name=None,
):
    if display_name is None:
        display_name = username

    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
            "display_name": display_name,
        },
    )


def login(client, email="user@example.com", password="password123"):
    return client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
