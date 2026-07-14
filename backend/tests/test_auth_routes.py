def test_login_succeeds_with_correct_credentials(client, make_staff_user):
    user, password = make_staff_user(email="staff@example.com", password="correct-password")

    response = client.post(
        "/auth/login", data={"username": "staff@example.com", "password": password}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_rejects_wrong_password(client, make_staff_user):
    make_staff_user(email="staff@example.com", password="correct-password")

    response = client.post(
        "/auth/login", data={"username": "staff@example.com", "password": "wrong-password"}
    )

    assert response.status_code == 401


def test_me_returns_current_user_with_valid_token(client, make_staff_user, issue_token, auth_headers):
    user, _ = make_staff_user(email="staff@example.com")
    token = issue_token(user)

    response = client.get("/auth/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["email"] == "staff@example.com"


def test_me_rejects_missing_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_rejects_invalid_token(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers("not-a-real-token"))
    assert response.status_code == 401


def test_register_creates_customer_and_returns_token(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "newcustomer@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "Customer",
        },
    )

    assert response.status_code == 201
    assert response.json()["access_token"]


def test_register_rejects_duplicate_email(client):
    payload = {
        "email": "dupe@example.com",
        "password": "password123",
        "first_name": "Dupe",
        "last_name": "One",
    }
    client.post("/auth/register", json=payload)

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400
