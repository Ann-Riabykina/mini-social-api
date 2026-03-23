def test_create_post_returns_author_and_likes_count(client, auth_headers):
    payload = {
        "title": "My first test post",
        "content": "Some content",
    }
    response = client.post("/api/v1/posts", json=payload, headers=auth_headers)

    assert response.status_code in (200, 201), response.text
    data = response.json()

    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert "author" in data
    assert "id" in data["author"]
    assert "email" in data["author"]
    assert "likes_count" in data
    assert data["likes_count"] == 0


def test_get_posts_list_returns_200(client):
    response = client.get("/api/v1/posts?limit=10&offset=0")

    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list) or isinstance(data, dict)


def test_post_details_returns_200(client, created_post):
    post_id = created_post["id"]

    response = client.get(f"/api/v1/posts/{post_id}")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == post_id
    assert "author" in data
    assert "likes_count" in data


def test_only_author_can_update_post(client, created_post, second_auth_headers):
    post_id = created_post["id"]

    payload = {
        "title": "Hacked title",
        "content": "Hacked content",
    }
    response = client.patch(
        f"/api/v1/posts/{post_id}",
        json=payload,
        headers=second_auth_headers,
    )

    assert response.status_code in (403, 404), response.text


def test_author_can_update_own_post(client, created_post, auth_headers):
    post_id = created_post["id"]

    payload = {
        "title": "Updated title",
        "content": "Updated content",
    }
    response = client.patch(
        f"/api/v1/posts/{post_id}",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]


def test_only_author_can_delete_post(client, created_post, second_auth_headers):
    post_id = created_post["id"]

    response = client.delete(
        f"/api/v1/posts/{post_id}",
        headers=second_auth_headers,
    )

    assert response.status_code in (403, 404), response.text


def test_like_is_idempotent(client, created_post, second_auth_headers):
    post_id = created_post["id"]

    first = client.post(
        f"/api/v1/posts/{post_id}/like",
        headers=second_auth_headers,
    )
    assert first.status_code == 200, first.text

    second = client.post(
        f"/api/v1/posts/{post_id}/like",
        headers=second_auth_headers,
    )
    assert second.status_code == 200, second.text

    details = client.get(f"/api/v1/posts/{post_id}")
    assert details.status_code == 200, details.text
    data = details.json()
    assert data["likes_count"] == 1


def test_unlike_is_idempotent(client, created_post, second_auth_headers):
    post_id = created_post["id"]

    like_response = client.post(
        f"/api/v1/posts/{post_id}/like",
        headers=second_auth_headers,
    )
    assert like_response.status_code == 200, like_response.text

    first = client.delete(
        f"/api/v1/posts/{post_id}/like",
        headers=second_auth_headers,
    )
    assert first.status_code == 200, first.text

    second = client.delete(
        f"/api/v1/posts/{post_id}/like",
        headers=second_auth_headers,
    )
    assert second.status_code == 200, second.text

    details = client.get(f"/api/v1/posts/{post_id}")
    assert details.status_code == 200, details.text
    data = details.json()
    assert data["likes_count"] == 0
