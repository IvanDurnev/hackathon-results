from io import BytesIO

from app.extensions import db
from app.modules.auth.services import create_user
from app.modules.files.models import FileAsset
from tests.conftest import login


def upload_file(client, file_name: str = "avatar.png", content: bytes = b"image-data", access_scope: str = "private"):
    return client.post(
        "/api/v1/files",
        data={
            "access_scope": access_scope,
            "file": (BytesIO(content), file_name),
        },
        content_type="multipart/form-data",
    )


def test_user_can_upload_files_with_same_original_name(client, app):
    with app.app_context():
        user = create_user("files-owner@example.com", "files-owner", "password123")
        email = user.email

    login(client, email, "password123")

    first = upload_file(client, "same-name.png", b"first")
    second = upload_file(client, "same-name.png", b"second")

    assert first.status_code == 201
    assert second.status_code == 201

    first_id = first.json["file"]["id"]
    second_id = second.json["file"]["id"]

    with app.app_context():
        first_asset = db.session.get(FileAsset, first_id)
        second_asset = db.session.get(FileAsset, second_id)

        assert first_asset is not None
        assert second_asset is not None
        assert first_asset.original_name == "same-name.png"
        assert second_asset.original_name == "same-name.png"
        assert first_asset.stored_name != second_asset.stored_name


def test_public_file_is_readable_without_auth(client, app):
    with app.app_context():
        user = create_user("public-owner@example.com", "public-owner", "password123")
        email = user.email

    login(client, email, "password123")
    response = upload_file(client, "public.png", b"public", access_scope="public")
    assert response.status_code == 201

    file_id = response.json["file"]["id"]
    client.post("/api/v1/auth/logout")

    response = client.get(f"/api/v1/files/{file_id}")
    assert response.status_code == 200
    assert response.data == b"public"


def test_private_file_is_hidden_from_other_users(client, app):
    with app.app_context():
        owner = create_user("private-owner@example.com", "private-owner", "password123")
        other = create_user("private-other@example.com", "private-other", "password123")
        owner_email = owner.email
        other_email = other.email

    login(client, owner_email, "password123")
    response = upload_file(client, "private.png", b"private", access_scope="private")
    assert response.status_code == 201
    file_id = response.json["file"]["id"]

    client.post("/api/v1/auth/logout")
    login(client, other_email, "password123")

    response = client.get(f"/api/v1/files/{file_id}")
    assert response.status_code == 403


def test_user_can_attach_uploaded_avatar(client, app):
    with app.app_context():
        user = create_user("avatar-owner@example.com", "avatar-owner", "password123")
        email = user.email

    login(client, email, "password123")
    uploaded = upload_file(client, "avatar.png", b"avatar-bytes", access_scope="private")
    assert uploaded.status_code == 201

    file_id = uploaded.json["file"]["id"]
    response = client.patch(
        "/api/v1/users/me",
        json={
            "display_name": "Avatar Owner",
            "avatar_file_id": file_id,
        },
    )

    assert response.status_code == 200
    assert response.json["user"]["display_name"] == "Avatar Owner"
    assert response.json["user"]["avatar"]["id"] == file_id
    assert response.json["user"]["avatar"]["access_scope"] == "public"

    with app.app_context():
        avatar_asset = db.session.get(FileAsset, file_id)
        assert avatar_asset is not None
        assert avatar_asset.access_scope == "public"


def test_user_can_clear_avatar_and_delete_file(client, app):
    with app.app_context():
        user = create_user("avatar-clear@example.com", "avatar-clear", "password123")
        email = user.email

    login(client, email, "password123")
    uploaded = upload_file(client, "avatar-clear.png", b"avatar-bytes", access_scope="private")
    assert uploaded.status_code == 201
    file_id = uploaded.json["file"]["id"]

    attached = client.patch(
        "/api/v1/users/me",
        json={
            "display_name": "Avatar Clear",
            "avatar_file_id": file_id,
        },
    )
    assert attached.status_code == 200
    assert attached.json["user"]["avatar"]["id"] == file_id

    response = client.patch(
        "/api/v1/users/me",
        json={
            "display_name": "Avatar Clear",
            "avatar_file_id": None,
        },
    )

    assert response.status_code == 200
    assert response.json["user"]["avatar"] is None

    with app.app_context():
        assert db.session.get(FileAsset, file_id) is None

    response = client.get(f"/api/v1/files/{file_id}")
    assert response.status_code == 404


def test_user_cannot_submit_blank_display_name(client, app):
    with app.app_context():
        user = create_user("blank-name@example.com", "blank-name", "password123")
        email = user.email

    login(client, email, "password123")

    response = client.patch(
        "/api/v1/users/me",
        json={
            "display_name": "   ",
        },
    )

    assert response.status_code == 422
    assert response.json["error"]["code"] == "validation_error"


def test_user_can_delete_own_file(client, app):
    with app.app_context():
        user = create_user("files-delete@example.com", "files-delete", "password123")
        email = user.email

    login(client, email, "password123")
    uploaded = upload_file(client, "delete-me.png", b"delete-me", access_scope="public")
    assert uploaded.status_code == 201

    file_id = uploaded.json["file"]["id"]
    response = client.delete(f"/api/v1/files/{file_id}")

    assert response.status_code == 200
    assert response.json["message"] == "File deleted."

    with app.app_context():
        assert db.session.get(FileAsset, file_id) is None

    response = client.get(f"/api/v1/files/{file_id}")
    assert response.status_code == 404
