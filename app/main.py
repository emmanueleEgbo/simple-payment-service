from fastapi import FastAPI

from app.api.v1.payment_routes import v1_router as payment_router


app = FastAPI(
    title="Payment Orchestration Service",
    version="1.0.0",
)

app.include_router(payment_router)

app.get("health")
async def health_check():
    return {"status": "healthy"}