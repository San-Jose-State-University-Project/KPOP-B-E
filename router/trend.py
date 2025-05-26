from fastapi import APIRouter
from service import trend_service as service

trend_router = APIRouter(prefix="/trend")

@trend_router.get("/{day}")
async def get_trend(day : str):
    response = await service.get_trend(day)
    return response

@trend_router.get("/artist/{artist_name}")
async def get_emotion_artist(artist_name : str):
    response = await service.get_emotion_by_artist(artist_name)
    return response

@trend_router.get("/song/{song_name}")
async def get_emotion_song(song_name : str):
    response = await service.get_emotion_by_song(song_name)
    return response

@trend_router.get("/kpop-subgenres/{day}")
async def get_genre_distribution(day : str):
    response = await service.get_genre_distribution(day)
    return response

@trend_router.get("/chart/{day}")
async def get_chart(day : str):
    print("start")
    response = await service.get_chart(day)
    return response


