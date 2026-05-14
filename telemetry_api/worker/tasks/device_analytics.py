from telemetry_api.database.database import AsyncSessionLocal
from telemetry_api.database.models import Measurement
from telemetry_api.worker.celery_app import celery_instance

import asyncio
import logging
import statistics
from collections import defaultdict
from datetime import datetime
from typing import Sequence

from sqlalchemy import select

logger = logging.getLogger(__name__)


async def _calculate_stats(values: Sequence[float]) -> dict[str, float | None]:
    """
    Возвращает статистику по набору чисел.

    Для пустого набора возвращает `None` во всех полях статистики.
    """

    if not values:
        return {
            "min": None,
            "max": None,
            "sum": None,
            "median": None,
        }

    return {
        "min": min(values),
        "max": max(values),
        "sum": sum(values),
        "median": statistics.median(values),
    }


async def async_generate_device_analytics(
    device_ids: Sequence[int],
    date_from_iso: str | None,
    date_to_iso: str | None,
) -> list[dict]:
    """
    Формирует агрегированную аналитику по списку устройств.

    Возвращает массив словарей формата `{device_id, count, x, y, z}`.
    """

    if not device_ids:
        logger.info("Analytics requested with empty device_ids")
        return []

    async with AsyncSessionLocal() as session:
        logger.info(
            "Generating analytics: devices=%s date_from=%s date_to=%s",
            list(device_ids),
            date_from_iso,
            date_to_iso,
        )
        stmt = select(Measurement).where(Measurement.device_id.in_(device_ids))

        if date_from_iso:
            stmt = stmt.where(Measurement.timestamp >= datetime.fromisoformat(date_from_iso))
        if date_to_iso:
            stmt = stmt.where(Measurement.timestamp <= datetime.fromisoformat(date_to_iso))

        result = await session.execute(stmt)
        measurements = result.scalars().all()

        logger.info("Fetched %s measurements", len(measurements))

        grouped_measurements = defaultdict(list)
        for measurement in measurements:
            grouped_measurements[measurement.device_id].append(measurement)

        analytics_results: list[dict] = []
        for device_id in device_ids:
            device_data: list = grouped_measurements.get(device_id, [])

            analytics_results.append(
                {
                    "device_id": device_id,
                    "count": len(device_data),
                    "x": await _calculate_stats([measurement.x for measurement in device_data]),
                    "y": await _calculate_stats([measurement.y for measurement in device_data]),
                    "z": await _calculate_stats([measurement.z for measurement in device_data]),
                }
            )

        logger.info("Generated analytics for %s devices", len(analytics_results))
        return analytics_results


@celery_instance.task(name="generate_analytics")
def generate_device_analytics_task(
    device_ids: Sequence[int],
    date_from_iso: str | None,
    date_to_iso: str | None,
):
    """
    Запускает асинхронную генерацию аналитики в контексте Celery.
    """

    logger.info(
        "Celery task started: devices=%s date_from=%s date_to=%s",
        list(device_ids),
        date_from_iso,
        date_to_iso,
    )

    result = asyncio.run(async_generate_device_analytics(device_ids, date_from_iso, date_to_iso))

    logger.info("Celery task finished: devices=%s result_items=%s", list(device_ids), len(result))
    return result
