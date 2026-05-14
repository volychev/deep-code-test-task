from telemetry_api.database.database import get_db
from telemetry_api.database.models import Device, User
from telemetry_api.schemas.devices import DeviceCreate, DeviceRead, DeviceUpdate

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, status

router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)


@router.post("/", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
async def create_device(device_in: DeviceCreate, db: AsyncSession = Depends(get_db)):
    if device_in.user_id is not None:
        owner = await db.get(User, device_in.user_id)

        if owner is None:
            raise HTTPException(status_code=404, detail="User not found")

    new_device = Device(**device_in.model_dump())
    db.add(new_device)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=404, detail="User not found")

    await db.refresh(new_device)
    return new_device


@router.get("/{device_id}", response_model=DeviceRead)
async def get_device(device_id: int, db: AsyncSession = Depends(get_db)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.patch("/{device_id}", response_model=DeviceRead)
async def update_device(device_id: int, device_in: DeviceUpdate, db: AsyncSession = Depends(get_db)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    update_data = device_in.model_dump(exclude_unset=True)

    if "user_id" in update_data and update_data["user_id"] is not None:
        owner = await db.get(User, update_data["user_id"])

        if owner is None:
            raise HTTPException(status_code=404, detail="User not found")

    for key, value in update_data.items():
        setattr(device, key, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=404, detail="User not found")

    await db.refresh(device)
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: int, db: AsyncSession = Depends(get_db)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    await db.delete(device)
    await db.commit()
    return None


@router.get("/", response_model=list[DeviceRead])
async def get_devices(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Device).order_by(Device.id).offset(offset).limit(limit))
    return result.scalars().all()
