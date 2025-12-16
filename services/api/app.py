from __future__ import annotations

from fastapi import FastAPI

from services.api.api import router as v1_router

app = FastAPI(
    title="Inclusive Credit Infrastructure API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(v1_router)


