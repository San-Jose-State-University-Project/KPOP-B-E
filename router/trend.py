from fastapi import APIRouter

trend_router = APIRouter(prefix="/trend")

@trend_router.get("/trend")
async def get_trend():

    return {"message": "Hello World"}
