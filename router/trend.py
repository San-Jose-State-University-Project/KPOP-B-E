from fastapi import APIRouter
from service import trend_service as service

trend_router = APIRouter(prefix="/trend")

@trend_router.get("/{day}")
async def get_trend(day : str):
    service.get_trend(day)
    return {"message": "Hello World"}
