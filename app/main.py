import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.payment_routes import v1_router as payment_router
from app.core.async_db import async_engine, Base
from app.models.payment import Payment
from app.models.idempotency_record import IdempotencyRecord

app = FastAPI(
    title="Payment Orchestration Service",
    version="1.0.0",
)

app.include_router(payment_router)

app.get("health")
async def health_check():
    return {"status": "healthy"}