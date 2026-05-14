from telemetry_api.config import config

import logging

from celery import Celery

REDIS_URL = f"redis://{config.redis_host.get_secret_value()}:{config.redis_port}/{config.redis_db}"

celery_instance = Celery(
    "telemetry_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "telemetry_api.worker.tasks.device_analytics",
    ],
)

celery_instance.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=config.celery_result_expires,
    worker_hijack_root_logger=False,
    worker_log_color=False,
    worker_redirect_stdouts=True,
    worker_redirect_stdouts_level="INFO",
    worker_log_format=(
        "[%(asctime)s: %(levelname)s/%(processName)s] "
        "%(name)s %(task_name)s[%(task_id)s]: %(message)s"
    ),
    worker_task_log_format=(
        "[%(asctime)s: %(levelname)s/%(processName)s] "
        "%(name)s %(task_name)s[%(task_id)s]: %(message)s"
    ),
)

logging.getLogger("celery").setLevel(logging.INFO)
