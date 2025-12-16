FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install -U pip

COPY pyproject.toml /app/pyproject.toml
COPY src /app/src
COPY services /app/services

RUN pip install -e ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "services.api.app:app", "--host", "0.0.0.0", "--port", "8000"]


