from telemetry_api.database.database import get_db
from telemetry_api.database.models import Device, Measurement
from telemetry_api.schemas.analytics import (
    AnalyticsFilters,
    DeviceStats,
    MeasurementCreate,
    MeasurementRead,
    StatsResponse,
    TaskResponse,
    TaskStatus,
)
from telemetry_api.worker.celery_app import celery_instance
from telemetry_api.worker.tasks.device_analytics import (
    async_generate_device_analytics,
    generate_device_analytics_task,
)

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


async def _resolve_device_ids(
    filters: AnalyticsFilters,
    db: AsyncSession,
    limit: int | None = None,
    offset: int | None = None,
) -> list[int]:
    """
    Возвращает идентификаторы устройств для построения аналитики.

    При `device_id` проверяет существование устройства.
    При `user_id` возвращает список устройств пользователя с учётом пагинации.
    """

    if filters.device_id is not None:
        device = await db.get(Device, filters.device_id)

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        if offset is not None and offset > 0:
            return []

        return [filters.device_id]

    if filters.user_id is not None:
        stmt = select(Device.id).where(Device.user_id == filters.user_id).order_by(Device.id)

        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    raise HTTPException(status_code=400, detail="Must provide either device_id or user_id")


async def _resolve_total_items(filters: AnalyticsFilters, db: AsyncSession) -> int:
    """
    Возвращает общее количество элементов до пагинации.

    Для `device_id` возвращает `1`, для `user_id` — число устройств пользователя.
    """

    total_items: int = 0

    if filters.device_id is None and filters.user_id is None:
        raise HTTPException(status_code=400, detail="Must provide either device_id or user_id")

    if filters.device_id is not None:
        total_items = 1

    elif filters.user_id is not None:
        count_stmt = select(func.count(Device.id)).where(Device.user_id == filters.user_id)
        total_items = await db.scalar(count_stmt) or 0

    if total_items == 0:
        raise HTTPException(status_code=404, detail="Target not found")

    return total_items


@router.post("/{device_id}/data", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
async def add_measurement(
    device_id: int,
    data: MeasurementCreate,
    db: AsyncSession = Depends(get_db),
):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    new_measurement = Measurement(**data.model_dump(), device_id=device_id)
    db.add(new_measurement)

    await db.commit()
    await db.refresh(new_measurement)
    return new_measurement


@router.get("/", response_model=StatsResponse, status_code=status.HTTP_200_OK)
async def get_analytics(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    filters: AnalyticsFilters = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает агрегированную аналитику по устройствам.

    Выполняет расчёт синхронно, применяет фильтры по пользователю/устройству и датам,
    и возвращает пагинированный результат.
    """

    total_items: int = await _resolve_total_items(filters, db)
    device_ids: list[int] = await _resolve_device_ids(filters, db, limit=limit, offset=offset)

    if not device_ids:
        return StatsResponse(
            total_items=total_items,
            limit=limit,
            offset=offset,
            data=[],
        )

    iso_from = filters.date_from.isoformat() if filters.date_from else None
    iso_to = filters.date_to.isoformat() if filters.date_to else None

    analytics_result = await async_generate_device_analytics(device_ids, iso_from, iso_to)

    return StatsResponse(
        total_items=total_items,
        limit=limit,
        offset=offset,
        data=[DeviceStats(**a) for a in analytics_result],
    )


@router.post("/generate", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_analytics(
    filters: AnalyticsFilters = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Запускает фоновую задачу генерации аналитики.

    Возвращает `task_id` для последующего опроса статуса задачи.
    """

    device_ids: list[int] = await _resolve_device_ids(filters, db)

    if not device_ids:
        raise HTTPException(status_code=404, detail="No devices found")

    iso_from = filters.date_from.isoformat() if filters.date_from else None
    iso_to = filters.date_to.isoformat() if filters.date_to else None

    task = generate_device_analytics_task.delay(device_ids, iso_from, iso_to)

    return TaskResponse(task_id=task.id, status=TaskStatus.PROCESSING)


@router.get("/tasks/{task_id}", response_model=StatsResponse | TaskResponse)
async def get_analytics_result(
    task_id: str,
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Возвращает результат или статус фоновой задачи аналитики.

    Для `SUCCESS` отдаёт данные статистики, для остальных статусов — служебный ответ.
    """

    task_result = celery_instance.AsyncResult(task_id)

    match task_result.state:
        case TaskStatus.PENDING:
            return TaskResponse(task_id=task_id, status=TaskStatus.PENDING)

        case TaskStatus.SUCCESS:
            results: list[dict] = task_result.result
            total_items: int = len(results)

            paginated_results: list[dict] = results[offset : offset + limit]

            return StatsResponse(
                total_items=total_items,
                limit=limit,
                offset=offset,
                data=[DeviceStats(**a) for a in paginated_results],
            )

        case TaskStatus.FAILURE:
            raise HTTPException(status_code=500, detail="Task failed during processing")

        case _:
            return TaskResponse(task_id=task_id, status=task_result.state)
