from httpx import AsyncClient

async def test_create_device(async_client: AsyncClient):
    user_response = await async_client.post(
        "/users/",
        json={"username": "device_owner", "email": "owner@example.com"}
    )
    user_id = user_response.json()["id"]

    response = await async_client.post(
        "/devices/",
        json={
            "name": "Temperature Sensor",
            "user_id": user_id
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Temperature Sensor"
    assert data["user_id"] == user_id
    assert "id" in data


async def test_get_device(async_client: AsyncClient):
    user_response = await async_client.post(
        "/users/",
        json={"username": "device_reader", "email": "reader@example.com"}
    )
    user_id = user_response.json()["id"]

    create_response = await async_client.post(
        "/devices/",
        json={
            "name": "Humidity Sensor",
            "user_id": user_id
        },
    )
    device_id = create_response.json()["id"]

    response = await async_client.get(f"/devices/{device_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Humidity Sensor"
    assert response.json()["user_id"] == user_id


async def test_update_device(async_client: AsyncClient):
    user_response = await async_client.post(
        "/users/",
        json={"username": "device_updater", "email": "updater@example.com"}
    )
    user_id = user_response.json()["id"]

    create_response = await async_client.post(
        "/devices/",
        json={
            "name": "Old Sensor Name",
            "user_id": user_id
        },
    )
    device_id = create_response.json()["id"]

    update_response = await async_client.patch(
        f"/devices/{device_id}",
        json={"name": "New Sensor Name"}
    )
    device = update_response.json()

    assert update_response.status_code == 200
    assert device["name"] == "New Sensor Name"
    assert device["user_id"] == user_id


async def test_delete_device(async_client: AsyncClient):
    user_response = await async_client.post(
        "/users/",
        json={"username": "device_deleter", "email": "deleter@example.com"}
    )
    user_id = user_response.json()["id"]

    create_response = await async_client.post(
        "/devices/",
        json={
            "name": "Sensor to Delete",
            "user_id": user_id
        },
    )
    device_id = create_response.json()["id"]

    delete_response = await async_client.delete(
        f"/devices/{device_id}",
    )

    assert delete_response.status_code == 204

    response = await async_client.get(f"/devices/{device_id}")

    assert response.status_code == 404


async def test_paginate_device(async_client: AsyncClient):
    user_response = await async_client.post(
        "/users/",
        json={"username": "device_list_user", "email": "list@example.com"}
    )
    user_id = user_response.json()["id"]

    create_response = await async_client.post(
        "/devices/",
        json={
            "name": "Paginated Sensor",
            "user_id": user_id
        },
    )
    device_id = create_response.json()["id"]

    list_response = await async_client.get(
        "/devices/",
        params={
            "limit": 1,
            "offset": 0
        },
    )

    data = list_response.json()
    assert len(data) == 1
    assert data[0]["id"] == device_id
