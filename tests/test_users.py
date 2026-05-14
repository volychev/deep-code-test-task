from httpx import AsyncClient

async def test_create_user(async_client: AsyncClient):
    response = await async_client.post(
        "/users/",
        json={
            "username": "kirill",
            "email": "kirill@example.com"
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "kirill"
    assert data["email"] == "kirill@example.com"
    assert "id" in data


async def test_get_user(async_client: AsyncClient):
    create_response = await async_client.post(
        "/users/",
        json={
            "username": "deep-code",
            "email": "deep-code@example.com"
        },
    )
    user_id = create_response.json()["id"]

    response = await async_client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["username"] == "deep-code"


async def test_update_user(async_client: AsyncClient):
    create_response = await async_client.post(
        "/users/",
        json={
            "username": "kirill",
            "email": "no-reply@example.com"
        },
    )
    user_id = create_response.json()["id"]

    update_response = await async_client.patch(
        f"/users/{user_id}",
        json={"email": "kirill@example.com"}
    )
    user = update_response.json()

    assert update_response.status_code == 200

    assert user["username"] == "kirill"
    assert user["email"] == "kirill@example.com"


async def test_delete_user(async_client: AsyncClient):
    create_response = await async_client.post(
        "/users/",
        json={
            "username": "kirill",
            "email": "kirill@example.com"
        },
    )
    user_id = create_response.json()["id"]

    delete_response = await async_client.delete(
        f"/users/{user_id}",
    )

    assert delete_response.status_code == 204

    response = await async_client.get(f"/users/{user_id}")

    assert response.status_code == 404


async def test_paginate_user(async_client: AsyncClient):
    create_response = await async_client.post(
        "/users/",
        json={
            "username": "deep-code",
            "email": "deep-code@example.com"
        },
    )
    user_id = create_response.json()["id"]

    list_response = await async_client.get(
        "/users/",
        params={
            "limit": 1,
            "offset": 0
        },
    )

    data = list_response.json()
    assert len(data) == 1
    assert data[0]["id"] == user_id


async def test_invalid_email(async_client: AsyncClient):
    create_response = await async_client.post(
        "/users/",
        json={
            "username": "admin",
            "email": "not-a-email"
        },
    )

    assert create_response.status_code == 422
