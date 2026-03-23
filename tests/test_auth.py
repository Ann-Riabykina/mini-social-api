def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_returns_201(client, user_payload):
    response = client.post("/api/v1/auth/register", json=user_payload)

    assert response.status_code == 201, response.text
    data = response.json()

    assert data["email"] == user_payload["email"]
    assert "password" not in data


def test_register_duplicate_email_returns_409(client, user_payload):
    first = client.post("/api/v1/auth/register", json=user_payload)
    assert first.status_code == 201, first.text

    second = client.post("/api/v1/auth/register", json=user_payload)
    assert second.status_code == 409, second.text


def test_login_returns_access_and_refresh_tokens(client, registered_user):
    response = client.post("/api/v1/auth/login", json=registered_user)

    assert response.status_code == 200, response.text
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data


def test_login_with_wrong_password_returns_401(client, registered_user):
    payload = {
        "email": registered_user["email"],
        "password": "WrongPassword123",
    }
    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 401, response.text


def test_invalid_register_data_returns_400(client):
    payload = {
        "email": "not-an-email",
        "password": "123",
    }
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 400, response.text


def test_protected_endpoint_without_token_returns_401(client):
    payload = {
        "title": "No auth post",
        "content": "Should fail",
    }
    response = client.post("/api/v1/posts", json=payload)

    assert response.status_code == 401, response.text
