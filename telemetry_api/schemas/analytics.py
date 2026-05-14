from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MeasurementBase(BaseModel):
    """
    Базовая схема измерения.
    """

    x: float = Field(..., description="Значение по оси X.", examples=[1.23])
    y: float = Field(..., description="Значение по оси Y.", examples=[4.56])
    z: float = Field(..., description="Значение по оси Z.", examples=[7.89])


class MeasurementCreate(MeasurementBase):
    """
    Схема создания измерения.
    """

    pass


class MeasurementRead(MeasurementBase):
    """
    Схема ответа с данными измерения.
    """

    id: int = Field(..., description="Уникальный идентификатор измерения.", examples=[100])
    device_id: int = Field(..., description="Идентификатор устройства.", examples=[10])
    timestamp: datetime = Field(
        ...,
        description="Момент записи измерения в формате ISO 8601.",
        examples=["2026-01-10T12:34:56Z"],
    )

    model_config = ConfigDict(from_attributes=True)


class AnalyticsFilters(BaseModel):
    """
    Схема фильтров аналитики.
    """

    device_id: int | None = Field(
        default=None,
        description="Идентификатор конкретного устройства для аналитики.",
        examples=[10],
    )
    user_id: int | None = Field(
        default=None,
        description="Идентификатор пользователя; аналитика строится по всем его устройствам.",
        examples=[1],
    )
    date_from: datetime | None = Field(
        default=None,
        description="Нижняя граница периода (включительно).",
        examples=["2026-01-01T00:00:00Z"],
    )
    date_to: datetime | None = Field(
        default=None,
        description="Верхняя граница периода (включительно).",
        examples=["2026-01-31T23:59:59Z"],
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        """
        Проверяет корректность диапазона дат.

        `date_from` не может быть позже `date_to`, если обе даты заданы.
        """

        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from cannot be after date_to")
        return self


class MeasurementStats(BaseModel):
    """
    Схема статистики по метрике.
    """

    min: float | None = Field(
        default=None,
        description="Минимальное значение по оси; None, если данных нет.",
        examples=[0.12],
    )
    max: float | None = Field(
        default=None,
        description="Максимальное значение по оси; None, если данных нет.",
        examples=[9.99],
    )
    sum: float | None = Field(
        default=None,
        description="Сумма значений по оси; None, если данных нет.",
        examples=[123.45],
    )
    median: float | None = Field(
        default=None,
        description="Медиана значений по оси; None, если данных нет.",
        examples=[4.56],
    )


class DeviceStats(BaseModel):
    """
    Схема агрегированной статистики устройства.
    """

    device_id: int = Field(..., description="Идентификатор устройства.", examples=[10])
    measurements_count: int = Field(
        ...,
        alias="count",
        validation_alias="count",
        serialization_alias="measurements_count",
        description="Количество измерений, вошедших в расчёт статистики.",
        examples=[42],
    )
    x: MeasurementStats = Field(..., description="Статистика по оси X.")
    y: MeasurementStats = Field(..., description="Статистика по оси Y.")
    z: MeasurementStats = Field(..., description="Статистика по оси Z.")


class StatsResponse(BaseModel):
    """
    Схема ответа со статистикой.
    """

    total_items: int = Field(
        ...,
        description="Общее число элементов до пагинации.",
        examples=[100],
    )
    limit: int = Field(..., description="Лимит пагинации.", examples=[25])
    offset: int = Field(..., description="Смещение пагинации.", examples=[0])
    data: list[DeviceStats] = Field(
        ...,
        description="Список статистики по устройствам на текущей странице.",
    )


class TaskStatus(StrEnum):
    """
    Схема статусов фоновой задачи.
    """

    PROCESSING = "PROCESSING"
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"


class TaskResponse(BaseModel):
    """
    Схема ответа со статусом фоновой задачи.
    """

    task_id: str = Field(..., description="Идентификатор задачи Celery.", examples=["abc123"])
    status: str = Field(..., description="Текущий статус задачи.", examples=["PROCESSING"])
