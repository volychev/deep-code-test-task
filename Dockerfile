FROM python:3.13.11
WORKDIR /usr/src/telemetry_api
COPY . .

RUN python -m pip install --upgrade pip
RUN python -m pip install poetry
RUN python -m poetry install --without dev
