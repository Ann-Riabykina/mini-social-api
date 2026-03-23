import os
import uuid

import httpx
import pytest

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=20.0) as client:
        yield client


def make_user_payload() -> dict[str, str]:
    unique = uuid.uuid4().hex[:10]
    return {
        "email": f"test_{unique}@example.com",
        "password": "Testpass123",
    }


@pytest.fixture
def user_payload():
    return make_user_payload()


@pytest.fixture
def second_user_payload():
    return make_user_payload()


@pytest.fixture
def registered_user(client, user_payload):
    response = client.post("/api/v1/auth/register", json=user_payload)
    assert response.status_code == 201, response.text
    return user_payload


@pytest.fixture
def auth_tokens(client, registered_user):
    response = client.post("/api/v1/auth/login", json=registered_user)
    assert response.status_code == 200, response.text

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    return data


@pytest.fixture
def auth_headers(auth_tokens):
    return {"Authorization": f"Bearer {auth_tokens['access_token']}"}


@pytest.fixture
def second_auth_headers(client, second_user_payload):
    register_response = client.post("/api/v1/auth/register", json=second_user_payload)
    assert register_response.status_code == 201, register_response.text

    login_response = client.post("/api/v1/auth/login", json=second_user_payload)
    assert login_response.status_code == 200, login_response.text

    tokens = login_response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
def created_post(client, auth_headers):
    payload = {
        "title": f"Post {uuid.uuid4().hex[:8]}",
        "content": "Hello from test",
    }
    response = client.post("/api/v1/posts", json=payload, headers=auth_headers)
    assert response.status_code in (200, 201), response.text

    data = response.json()
    assert "id" in data
    return data
