from telemetry_api.api import api as app
from telemetry_api.config import config
from telemetry_api.database import models  # ! do not delete
from telemetry_api.database.database import Base, engine

from contextlib import asynccontextmanager
import uvicorn


@asynccontextmanager
async def lifespan(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app.router.lifespan_context = lifespan

if __name__ == "__main__":
    uvicorn.run("main:app", host=config.host, port=config.port, reload=True)
