from telemetry_api.database.database import get_db
from telemetry_api.database.models import Measurement, Device
from telemetry_api.schemas.analytics import MeasurementCreate, MeasurementRead

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.post("/{device_id}/data", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
async def add_measurement(device_id: int, data: MeasurementCreate, db: AsyncSession = Depends(get_db)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    new_measurement = Measurement(**data.model_dump(), device_id=device_id)
    db.add(new_measurement)

    await db.commit()
    await db.refresh(new_measurement)
    return new_measurement


# TODO: analytics
