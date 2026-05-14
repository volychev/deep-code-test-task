from pydantic import BaseModel, ConfigDict
from datetime import datetime


class MeasurementBase(BaseModel):
    x: float
    y: float
    z: float


class MeasurementCreate(MeasurementBase):
    pass


class MeasurementRead(MeasurementBase):
    id: int
    device_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
