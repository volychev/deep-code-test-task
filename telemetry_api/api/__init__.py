from fastapi import APIRouter, FastAPI

from telemetry_api.api.v1 import analytics, devices, users
from telemetry_api.config import config


def create_api() -> FastAPI:
    """
    Создаёт и настраивает экземпляр FastAPI-приложения.
    """

    api = FastAPI(
        title="Telemetry API",
        description="",
        version="1.0.0",
    )

    api_router = APIRouter(prefix=config.api_prefix.rstrip("/"))
    v1_router = APIRouter(prefix=f"/{config.default_api_version.strip('/')}")

    v1_router.include_router(analytics.router)
    v1_router.include_router(devices.router)
    v1_router.include_router(users.router)

    api_router.include_router(v1_router)
    api.include_router(api_router)
    return api


api = create_api()
