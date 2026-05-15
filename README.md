# telemetry-api
![Python](https://img.shields.io/badge/Python-ffffff?logo=python&style=for-the-badge&color=ffffff&logoColor=3776AB) ![FastAPI](https://img.shields.io/badge/FastAPI-ffffff?logo=fastapi&style=for-the-badge&color=ffffff&logoColor=009688) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-ffffff?logo=postgresql&style=for-the-badge&color=ffffff&logoColor=4169E1) ![Redis](https://img.shields.io/badge/Redis-ffffff?logo=redis&style=for-the-badge&color=ffffff&logoColor=DC382D) ![Celery](https://img.shields.io/badge/Celery-ffffff?logo=celery&style=for-the-badge&color=ffffff&logoColor=37814A) ![Locust](https://img.shields.io/badge/Locust-ffffff?style=for-the-badge&color=ffffff) ![Docker](https://img.shields.io/badge/Docker-ffffff?logo=docker&style=for-the-badge&color=ffffff&logoColor=2496ED)

> **telemetry-api** - сервис для сбора, хранения и аналитики телеметрии с устройств с функционалом фоновых вычислений и привязкой к пользователям. Сервис реализован на Python и представляет собой REST Api, написанную с использованием фреймворка FastAPI. Хранение данных в PostgreSQL, фоновые вычисления при помощи Celery, кэширование и backend для фоновых вычислений — Redis.

#### [Техническое задание](task.md)

## Структура проекта:
```
.
├── .github                          # CI/CD для удалённого тестирования
│   └── workflows
│       └── ci.yml
├── telemetry_api                    
│   ├── api/v1                       # Основные роутеры 
│   │   ├── __init__.py              # Инициализация FastAPI и подключение роутеров
│   │   ├── analytics.py
│   │   ├── devices.py
│   │   └── users.py
│   ├── database                     # Инициализация БД исходя из режима
│   │   ├── database.py
│   │   └── models.py                # Модели БД
│   ├── schemas                      # Pydantic модели для сериализации и десериализации входных и выходных данных
│   │   ├── analytics.py
│   │   ├── devices.py
│   │   └── users.py
│   ├── worker                       
│   │   ├── celery_app.py            # Конфигурация Celery
│   │   └── tasks
│   │       └── device_analytics.py  # Такси для фоновых вычислений аналитики
│   ├── config.py                    # Конфиг, основанный на переменных окружения
│   └── main.py                      # Инициализация БД, моделей и запуск сервиса
├── tests                            # Тестирование основных роутеров и эндпоинтов
│   ├── conftest.py                  # Настройка и инициализация фикстур
│   ├── test_analytics.py
│   ├── test_devices.py
│   └── test_users.py
├── docker-compose.yml               # Развёртывания БД, Redis, Celery-worker и сервиса
├── Dockerfile
├── .env.example                     # Шаблонный файл переменных окружения
├── .gitignore
├── locustfile.py                    # Реализация нагрузочного тестирования через locust
├── poetry.lock
├── .pre-commit-config.yaml
├── pyproject.toml                   # Настройка проекта и библиотек
├── pytest.ini                       
├── README.md                        # Описание проекта
├── setup.cfg
└── task.md                          # Техническое задание
```

## Endpoints:
Базовый префикс API: `/api`
Текущая версия: `/v1`

* `POST`: `/api/v1/users/` — Создание нового пользователя
* `GET`: `/api/v1/users/{user_id}` — Получение пользователя по id
* `PATCH`: `/api/v1/users/{user_id}` — Частичное обновление данных пользователя
* `DELETE`: `/api/v1/users/{user_id}` — Удаление пользователя
* `GET`: `/api/v1/users/` — Получение списка пользователей с пагинацией
<br>

* `POST`: `/api/v1/devices/` — Создание нового устройства (с возможностью привязки к пользователю)
* `GET`: `/api/v1/devices/{device_id}` — Получение устройства по id
* `PATCH`: `/api/v1/devices/{device_id}` — Частичное обновление данных устройства (включая смену владельца)
* `DELETE`: `/api/v1/devices/{device_id}` — Удаление устройства
* `GET`: `/api/v1/devices/` — Получение списка устройств с пагинацией
<br>

* `POST`: `/api/v1/analytics/{device_id}/data` — Добавление одного измерения для конкретного устройства
* `GET`: `/api/v1/analytics/` — Получение агрегированной аналитики по устройству или пользователю (с возможностью фильтрации по времени и пагинацией)
* `POST`: `/api/v1/analytics/generate` — Запуск фоновой задачи через Celery для генерации аналитики асинхронно
* `GET`: `/api/v1/analytics/tasks/{task_id}` — Получение статуса или готового (пагинированного) результата фоновой задачи генерации аналитики
<br>

* `GET`: `/docs/` — Подробная документация с описанием нетривиальных функций и примерами данных

## Требования:
* Python 3.13.11+
* Poetry
* Docker & Docker Compose
* PostgreSQL
* Redis
* Celery

## Использование:
Необходимо указать переменные окружения в `.env` [*(Шаблон)*](.env.example):
```env
# Common
DEBUG=True                    # Режим отладки. Используется SQLite 
HOST=0.0.0.0              
PORT=8000
CELERY_RESULT_EXPIRES=43200   # Таймаут, после которого удаляется результат выполнения таски Celery

# PostgreSQL
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DB=

# Redis
REDIS_HOST=
REDIS_PORT=
REDIS_DB=
```

Развёртывание при помощи `docker-compose`:
```
docker compose up -d --build
```
