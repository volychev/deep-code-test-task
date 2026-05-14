from pydantic import BaseModel, ConfigDict


class DeviceBase(BaseModel):
    name: str


class DeviceCreate(DeviceBase):
    user_id: int | None = None


class DeviceUpdate(BaseModel):
    name: str | None = None
    user_id: int | None = None


class DeviceRead(DeviceBase):
    id: int
    user_id: int | None

    model_config = ConfigDict(from_attributes=True)
