# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY app ./app

CMD ["celery", "-A", "app.worker", "worker", "-l", "info"]
