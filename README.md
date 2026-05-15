# telemetry-api
![Python](https://img.shields.io/badge/Python-ffffff?logo=python&style=for-the-badge&color=ffffff&logoColor=3776AB) ![FastAPI](https://img.shields.io/badge/FastAPI-ffffff?logo=fastapi&style=for-the-badge&color=ffffff&logoColor=009688) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-ffffff?logo=postgresql&style=for-the-badge&color=ffffff&logoColor=4169E1) ![Redis](https://img.shields.io/badge/Redis-ffffff?logo=redis&style=for-the-badge&color=ffffff&logoColor=DC382D) ![Celery](https://img.shields.io/badge/Celery-ffffff?logo=celery&style=for-the-badge&color=ffffff&logoColor=37814A) ![Locust](https://img.shields.io/badge/Locust-ffffff?style=for-the-badge&color=ffffff) ![Docker](https://img.shields.io/badge/Docker-ffffff?logo=docker&style=for-the-badge&color=ffffff&logoColor=2496ED)

**telemetry-api** — асинхронный REST API сервис для сбора, хранения и анализа телеметрии с устройств. Включает в себя механизмы фоновых вычислений, кэширования, валидацию данных и систему управления пользователями.

* #### [Техническое задание](task.md)

Основная логика разделена на два сценария. Синхронный эндпоинт используется для быстрой обработки небольших данных. Для тяжелых аналитик реализован запуск фоновой задачи через **Celery + Redis**, что позволяет не блокировать основной пул потоков HTTP-запросов. Результаты задач кэшируются с пагинацией.

## Структура проекта:
```text
.
├── .github                          # CI/CD для автоматического тестирования
│   └── workflows
│       └── ci.yml
├── telemetry_api                    
│   ├── api/v1                       # Основные роутеры 1-й версии API
│   │   ├── __init__.py              # Инициализация приложения и подключение роутеров
│   │   ├── analytics.py
│   │   ├── devices.py
│   │   └── users.py
│   ├── database                     # Конфигурация подключения к БД
│   │   ├── database.py
│   │   └── models.py                # ORM-модели SQLAlchemy
│   ├── schemas                      # Pydantic-модели (валидация, сериализация/десериализация)
│   │   ├── analytics.py
│   │   ├── devices.py
│   │   └── users.py
│   ├── worker                       
│   │   ├── celery_app.py            # Конфигурация брокера и бэкенда Celery
│   │   └── tasks
│   │       └── device_analytics.py  # Таски для фоновых вычислений аналитики
│   ├── config.py                    # Валидация переменных окружения (pydantic-settings)
│   └── main.py                      # Точка входа
├── tests                            # Интеграционные и юнит-тесты (Pytest)
│   ├── conftest.py                  # Асинхронные фикстуры и настройка тестовой БД
│   ├── test_analytics.py
│   ├── test_devices.py
│   └── test_users.py
├── locustfile.py                    # Сценарии нагрузочного тестирования (Locust)
├── pyproject.toml                   # Конфигурация проекта (Poetry)
├── poetry.lock
├── .env.example                     # Шаблон переменных окружения
├── Dockerfile
├── docker-compose.yml               # Оркестрация (API, PostgreSQL, Redis, Celery-worker)     
├── pytest.ini                       # Конфигурация тестирования
├── setup.cfg                        # Конфигурация шаблонного проекта
├── .gitignore
├── .pre-commit-config.yaml
├── README.md                        # Описание проекта
└── task.md                          # Техническое задание 
```

## Endpoints

> *Полная спецификация, схемы и примеры данных доступны локально по адресу:* `http://localhost:{PORT}/docs` *(Swagger UI).*

Базовый префикс API: `/api` ; Текущая версия: `/v1`

### Пользователи (`Users`)

* `POST`: `/api/v1/users/` — Создание нового пользователя
* `GET`: `/api/v1/users/{user_id}` — Получение пользователя по id
* `PATCH`: `/api/v1/users/{user_id}` — Частичное обновление данных пользователя (с валидацией уникальности)
* `DELETE`: `/api/v1/users/{user_id}` — Удаление пользователя
* `GET`: `/api/v1/users/` — Получение списка пользователей с пагинацией

### Устройства (`Devices`)

* `POST`: `/api/v1/devices/` — Создание нового устройства (с возможностью привязки к `user_id`)
* `GET`: `/api/v1/devices/{device_id}` — Получение устройства по id
* `PATCH`: `/api/v1/devices/{device_id}` — Частичное обновление данных устройства (включая смену владельца)
* `DELETE`: `/api/v1/devices/{device_id}` — Удаление устройства
* `GET`: `/api/v1/devices/` — Получение списка устройств с пагинацией

### Аналитика (`Analytics`)

* `POST`: `/api/v1/analytics/{device_id}/data` — Добавление одного измерения для конкретного устройства
* `GET`: `/api/v1/analytics/` — Получение агрегированной аналитики (min, max, count, sum, median) по устройству или пользователю (с фильтрацией по времени и пагинацией)
* `POST`: `/api/v1/analytics/generate` — Запуск фоновой задачи через Celery для асинхронной генерации аналитики
* `GET`: `/api/v1/analytics/tasks/{task_id}` — Получение статуса или готового результата (с пагинацией) фоновой задачи

## Требования

* Python 3.13.11+
* Poetry
* Docker & Docker Compose
* PostgreSQL
* Redis
* Celery

## Развертывание и использование

1. Склонируйте репозиторий и укажите переменные окружения в файле `.env` на основе шаблона *[(.env.example)](.env.example)*:

```env
# Common
DEBUG=True                    # Режим отладки (Используется in-memory SQLite) 
HOST=0.0.0.0                  
PORT=8000
CELERY_RESULT_EXPIRES=43200   # Время жизни результатов тасок Celery в Redis (в секундах)

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

2. Запустите проект при помощи `docker-compose`:

```bash
docker compose up -d --build
```
