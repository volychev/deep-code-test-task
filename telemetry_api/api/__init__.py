from fastapi import FastAPI

from telemetry_api.api import analytics, devices, users


def create_api() -> FastAPI:
    """
    Создание инстенса приложения с подключением всех роутеров

    Return:
        FastAPI - инстанс приложения
    """

    api = FastAPI(
        title="Telemetry API",
        description="",
        version="1.0.0"
    )

    api.include_router(analytics.router)
    api.include_router(devices.router)
    api.include_router(users.router)
    return api


api = create_api()
