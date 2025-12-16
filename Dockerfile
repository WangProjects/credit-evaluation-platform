FROM python:3.11-slim

WORKDIR /app

# System deps (kept minimal)
RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml README.md LICENSE NOTICE /app/
COPY src /app/src

RUN pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLG_HOST=0.0.0.0 \
    FLG_PORT=8000

EXPOSE 8000

CMD ["python", "-m", "flg.api.main"]
