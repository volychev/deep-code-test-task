from httpx import AsyncClient

from conftest import api_path


async def _create_user(async_client: AsyncClient, username: str, email: str) -> dict:
    response = await async_client.post(
        api_path("/users/"),
        json={"username": username, "email": email},
    )

    assert response.status_code == 201
    return response.json()


async def test_create_user(async_client: AsyncClient):
    """
    Проверяет создание сущности.

    Ожидает успешный ответ и возврат идентификатора созданного объекта.
    """

    data = await _create_user(async_client, "kirill", "kirill@example.com")

    assert data["username"] == "kirill"
    assert data["email"] == "kirill@example.com"
    assert "id" in data


async def test_get_user(async_client: AsyncClient):
    """
    Проверяет получение сущности по идентификатору.

    Ожидает успешный ответ и корректные данные сохранённого объекта.
    """

    user = await _create_user(async_client, "deep-code", "deep-code@example.com")

    users_url = api_path("/users/").rstrip("/")
    response = await async_client.get(f"{users_url}/{user['id']}")

    assert response.status_code == 200
    assert response.json()["username"] == "deep-code"


async def test_update_user(async_client: AsyncClient):
    """
    Проверяет частичное обновление сущности.

    Ожидает обновление переданного поля и сохранение остальных полей без изменений.
    """

    user = await _create_user(async_client, "kirill", "no-reply@example.com")

    users_url = api_path("/users/").rstrip("/")
    update_response = await async_client.patch(f"{users_url}/{user['id']}", json={"email": "kirill@example.com"})
    updated_user = update_response.json()

    assert update_response.status_code == 200
    assert updated_user["username"] == "kirill"
    assert updated_user["email"] == "kirill@example.com"


async def test_update_exists_username(async_client: AsyncClient):
    """
    Проверяет обновление имени пользователя на уже существующее.

    Ожидает ошибку 409 при передаче существующего username.
    """

    first_user = await _create_user(async_client, "kirill", "kirill@example.com")
    second_user = await _create_user(async_client, "deep-code", "no-reply@example.com")

    users_url = api_path("/users/").rstrip("/")
    update_response = await async_client.patch(f"{users_url}/{second_user['id']}", json={"username": first_user["username"]})

    assert update_response.status_code == 409


async def test_delete_user(async_client: AsyncClient):
    """
    Проверяет удаление сущности.

    Ожидает недоступность объекта при последующем чтении.
    """

    user = await _create_user(async_client, "kirill", "kirill@example.com")

    users_url = api_path("/users/").rstrip("/")
    delete_response = await async_client.delete(f"{users_url}/{user['id']}")
    assert delete_response.status_code == 204

    response = await async_client.get(f"{users_url}/{user['id']}")
    assert response.status_code == 404


async def test_paginate_user(async_client: AsyncClient):
    """
    Проверяет выдачу списка с пагинацией.

    Ожидает, что параметры `limit` и `offset` корректно ограничивают результат
    и возвращают стабильный порядок элементов.
    """

    first_user = await _create_user(async_client, "user-1", "user-1@example.com")
    second_user = await _create_user(async_client, "user-2", "user-2@example.com")

    first_response = await async_client.get(
        api_path("/users/"),
        params={"limit": 1, "offset": 0},
    )
    second_response = await async_client.get(
        api_path("/users/"),
        params={"limit": 1, "offset": 1},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first = first_response.json()
    second = second_response.json()

    assert len(first) == 1
    assert len(second) == 1
    assert first[0]["id"] == first_user["id"]
    assert second[0]["id"] == second_user["id"]


async def test_invalid_email(async_client: AsyncClient):
    """
    Проверяет валидацию входных данных.

    Ожидает ошибку 422 при передаче невалидного email.
    """

    create_response = await async_client.post(
        api_path("/users/"),
        json={
            "username": "admin",
            "email": "not-a-email",
        },
    )

    assert create_response.status_code == 422
