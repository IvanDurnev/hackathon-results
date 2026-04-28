import pytest

from app import create_app
from app.core.security import make_stored_filename


def test_stored_filename_keeps_user_path_out():
    stored_name = make_stored_filename("../dangerous.txt")
    assert ".." not in stored_name
    assert "/" not in stored_name
    assert stored_name.endswith(".txt")


def test_production_requires_env_secret(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")


def test_production_uses_runtime_secret(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "runtime-secret")
    app = create_app("production", {"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    assert app.config["SECRET_KEY"] == "runtime-secret"
    assert app.config["SESSION_COOKIE_SECURE"] is True
