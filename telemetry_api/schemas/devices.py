from pydantic import BaseModel, ConfigDict, Field


class DeviceBase(BaseModel):
    """
    Базовая схема устройства.
    """

    name: str = Field(
        ...,
        description="Имя устройства.",
        examples=["Temperature Sensor"],
    )


class DeviceCreate(DeviceBase):
    """
    Схема создания устройства.
    """

    user_id: int | None = Field(
        default=None,
        description="Идентификатор владельца устройства; может отсутствовать.",
        examples=[1],
    )


class DeviceUpdate(BaseModel):
    """
    Схема частичного обновления устройства.
    """

    name: str | None = Field(
        default=None,
        description="Новое имя устройства; если не передано, поле не изменяется.",
        examples=["Humidity Sensor"],
    )
    user_id: int | None = Field(
        default=None,
        description="Новый идентификатор владельца; None отвязывает устройство от пользователя.",
        examples=[2],
    )


class DeviceRead(DeviceBase):
    """
    Схема ответа с данными устройства.
    """

    id: int = Field(
        ...,
        description="Уникальный идентификатор устройства.",
        examples=[10],
    )
    user_id: int | None = Field(
        ...,
        description="Идентификатор владельца устройства или None.",
        examples=[1],
    )

    model_config = ConfigDict(from_attributes=True)
