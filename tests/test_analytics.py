from httpx import AsyncClient

from conftest import api_path


async def _create_user(async_client: AsyncClient) -> int:
    response = await async_client.post(
        api_path("/users/"),
        json={"username": "kirill", "email": "kirill@example.com"},
    )
    return response.json()["id"]


async def _create_device(async_client: AsyncClient, name: str, user_id: int) -> int:
    response = await async_client.post(
        api_path("/devices/"),
        json={"name": name, "user_id": user_id},
    )
    return response.json()["id"]


async def test_add_measurement(async_client: AsyncClient):
    """
    Проверяет создание сущности.

    Ожидает успешный ответ и возврат идентификатора созданного объекта.
    """

    user_id = await _create_user(async_client)
    device_id = await _create_device(async_client, "Analytics Device", user_id)

    analytics_url = api_path("/analytics/").rstrip("/")
    response = await async_client.post(f"{analytics_url}/{device_id}/data", json={"x": 1.5, "y": 2.5, "z": 3.5})

    assert response.status_code == 201
    data = response.json()
    assert data["device_id"] == device_id
    assert data["x"] == 1.5
    assert data["y"] == 2.5
    assert data["z"] == 3.5
    assert "id" in data
    assert "timestamp" in data


async def test_add_measurement_device_not_found(async_client: AsyncClient):
    """
    Проверяет обработку чтения несуществующей сущности.

    Ожидает код 404 при обращении к отсутствующему объекту.
    """

    analytics_url = api_path("/analytics/").rstrip("/")
    response = await async_client.post(f"{analytics_url}/999999/data", json={"x": 1.0, "y": 2.0, "z": 3.0})

    assert response.status_code == 404


async def test_get_analytics_by_device(async_client: AsyncClient):
    """
    Проверяет получение аналитики по идентификатору сущности.

    Ожидает успешный ответ с корректной пагинацией и статистикой.
    """

    user_id = await _create_user(async_client)
    device_id = await _create_device(async_client, "Analytics Reader Device", user_id)

    analytics_url = api_path("/analytics/").rstrip("/")
    await async_client.post(f"{analytics_url}/{device_id}/data", json={"x": 1.0, "y": 2.0, "z": 3.0})
    await async_client.post(f"{analytics_url}/{device_id}/data", json={"x": 3.0, "y": 4.0, "z": 5.0})

    response = await async_client.get(
        api_path("/analytics/"),
        params={"device_id": device_id, "limit": 25, "offset": 0},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 1
    assert data["limit"] == 25
    assert data["offset"] == 0
    assert len(data["data"]) == 1

    stats = data["data"][0]
    assert stats["device_id"] == device_id
    assert stats["measurements_count"] == 2
    assert stats["x"] == {"min": 1.0, "max": 3.0, "sum": 4.0, "median": 2.0}
    assert stats["y"] == {"min": 2.0, "max": 4.0, "sum": 6.0, "median": 3.0}
    assert stats["z"] == {"min": 3.0, "max": 5.0, "sum": 8.0, "median": 4.0}


async def test_get_analytics_by_user_uses_stable_pagination(async_client: AsyncClient):
    """
    Проверяет выдачу списка с пагинацией.

    Ожидает, что параметры `limit` и `offset` корректно ограничивают результат.
    """

    user_id = await _create_user(async_client)
    first_device_id = await _create_device(async_client, "Device A", user_id)
    second_device_id = await _create_device(async_client, "Device B", user_id)

    analytics_url = api_path("/analytics/").rstrip("/")
    await async_client.post(f"{analytics_url}/{first_device_id}/data", json={"x": 1.0, "y": 1.0, "z": 1.0})
    await async_client.post(f"{analytics_url}/{second_device_id}/data", json={"x": 2.0, "y": 2.0, "z": 2.0})

    first_page_response = await async_client.get(
        api_path("/analytics/"),
        params={"user_id": user_id, "limit": 1, "offset": 0},
    )
    second_page_response = await async_client.get(
        api_path("/analytics/"),
        params={"user_id": user_id, "limit": 1, "offset": 1},
    )

    assert first_page_response.status_code == 200
    assert second_page_response.status_code == 200

    first_page = first_page_response.json()
    second_page = second_page_response.json()

    assert first_page["total_items"] == 2
    assert second_page["total_items"] == 2
    assert first_page["data"][0]["device_id"] == first_device_id
    assert second_page["data"][0]["device_id"] == second_device_id


async def test_get_analytics_requires_filter(async_client: AsyncClient):
    """
    Проверяет валидацию входных данных.

    Ожидает ошибку 400 при отсутствии обязательного фильтра запроса.
    """

    response = await async_client.get(api_path("/analytics/"))
    assert response.status_code == 400


async def test_get_analytics_validates_limit_and_offset(async_client: AsyncClient):
    """
    Проверяет валидацию входных данных.

    Ожидает ошибку 422 при некорректных параметрах пагинации.
    """

    response = await async_client.get(
        api_path("/analytics/"),
        params={"device_id": 1, "limit": 0, "offset": -1},
    )

    assert response.status_code == 422


async def test_generate_analytics_route_not_conflicting(async_client: AsyncClient):
    """
    Проверяет роутинг служебной ручки генерации аналитики.

    Ожидает бизнес-ошибку фильтров, а не парсинг `generate` как `device_id`.
    """

    response = await async_client.post(api_path("/analytics/generate"))

    assert response.status_code == 400
