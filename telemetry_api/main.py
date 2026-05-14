from telemetry_api.api import api as app
from telemetry_api.database.database import engine, Base
from telemetry_api.database import models

import uvicorn
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app.router.lifespan_context = lifespan

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
