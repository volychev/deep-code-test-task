from httpx import AsyncClient

from conftest import api_path


async def _create_user(async_client: AsyncClient) -> int:
    response = await async_client.post(
        api_path("/users/"),
        json={"username": "kirill", "email": "kirill@example.com"},
    )
    return response.json()["id"]


async def _create_device(async_client: AsyncClient, name: str, user_id: int | None) -> dict:
    response = await async_client.post(
        api_path("/devices/"),
        json={"name": name, "user_id": user_id},
    )

    assert response.status_code == 201
    return response.json()


async def test_create_device(async_client: AsyncClient):
    """
    Проверяет создание сущности.

    Ожидает успешный ответ и возврат идентификатора созданного объекта.
    """

    owner_id = await _create_user(async_client)
    data = await _create_device(async_client, "Temperature Sensor", owner_id)

    assert data["name"] == "Temperature Sensor"
    assert data["user_id"] == owner_id
    assert "id" in data


async def test_create_device_without_owner(async_client: AsyncClient):
    """
    Проверяет создание сущности без пользователя.

    Ожидает успешный ответ и возврат идентификатора созданного объекта.
    """

    data = await _create_device(async_client, "Temperature Sensor", None)

    assert data["name"] == "Temperature Sensor"
    assert data["user_id"] is None
    assert "id" in data


async def test_get_device(async_client: AsyncClient):
    """
    Проверяет получение сущности по идентификатору.

    Ожидает успешный ответ и корректные данные сохранённого объекта.
    """

    owner_id = await _create_user(async_client)
    device = await _create_device(async_client, "Humidity Sensor", owner_id)

    devices_url = api_path("/devices/").rstrip("/")
    response = await async_client.get(f"{devices_url}/{device['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Humidity Sensor"
    assert response.json()["user_id"] == owner_id


async def test_update_device(async_client: AsyncClient):
    """
    Проверяет частичное обновление сущности.

    Ожидает обновление переданного поля и сохранение остальных полей без изменений.
    """

    owner_id = await _create_user(async_client)
    device = await _create_device(async_client, "Old Sensor Name", owner_id)

    devices_url = api_path("/devices/").rstrip("/")
    update_response = await async_client.patch(f"{devices_url}/{device['id']}", json={"name": "New Sensor Name"})
    updated_device = update_response.json()

    assert update_response.status_code == 200
    assert updated_device["name"] == "New Sensor Name"
    assert updated_device["user_id"] == owner_id


async def test_delete_device(async_client: AsyncClient):
    """
    Проверяет удаление сущности.

    Ожидает недоступность объекта при последующем чтении.
    """

    owner_id = await _create_user(async_client)
    device = await _create_device(async_client, "Sensor to Delete", owner_id)

    devices_url = api_path("/devices/").rstrip("/")
    delete_response = await async_client.delete(f"{devices_url}/{device['id']}")
    assert delete_response.status_code == 204

    response = await async_client.get(f"{devices_url}/{device['id']}")
    assert response.status_code == 404


async def test_paginate_device(async_client: AsyncClient):
    """
    Проверяет выдачу списка с пагинацией.

    Ожидает, что параметры `limit` и `offset` корректно ограничивают результат
    и возвращают стабильный порядок элементов.
    """

    owner_id = await _create_user(async_client)
    first_device = await _create_device(async_client, "Paginated Sensor 1", owner_id)
    second_device = await _create_device(async_client, "Paginated Sensor 2", owner_id)

    first_response = await async_client.get(
        api_path("/devices/"),
        params={"limit": 1, "offset": 0},
    )
    second_response = await async_client.get(
        api_path("/devices/"),
        params={"limit": 1, "offset": 1},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first = first_response.json()
    second = second_response.json()

    assert len(first) == 1
    assert len(second) == 1
    assert first[0]["id"] == first_device["id"]
    assert second[0]["id"] == second_device["id"]
