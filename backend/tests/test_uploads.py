from unittest.mock import MagicMock, patch

from app.models import UserRole


def test_upload_requires_auth(client):
    response = client.post("/uploads", files={"file": ("photo.png", b"fake-bytes", "image/png")})
    assert response.status_code == 401


def test_upload_rejects_customer_role(client, make_customer, issue_token, auth_headers):
    _, user, _ = make_customer()
    token = issue_token(user)

    response = client.post(
        "/uploads",
        files={"file": ("photo.png", b"fake-bytes", "image/png")},
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_upload_rejects_non_image_content_type(client, make_staff_user, issue_token, auth_headers):
    user, _ = make_staff_user(role=UserRole.STAFF)
    token = issue_token(user)

    response = client.post(
        "/uploads",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers=auth_headers(token),
    )

    assert response.status_code == 400


@patch("app.core.storage.get_s3_client")
def test_upload_succeeds_for_staff_and_returns_public_url(
    mock_get_client, client, make_staff_user, issue_token, auth_headers
):
    mock_get_client.return_value = MagicMock()

    user, _ = make_staff_user(role=UserRole.STAFF)
    token = issue_token(user)

    response = client.post(
        "/uploads",
        files={"file": ("photo.png", b"fake-bytes", "image/png")},
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["url"].endswith(".png")
    assert "/products/" in body["url"]
    mock_get_client.return_value.put_object.assert_called_once()
