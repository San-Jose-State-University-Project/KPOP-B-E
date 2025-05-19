import json
from datetime import datetime, timedelta

from data.analyze.download_chart import DownloadChart as download_chart
from data.analyze.trend_analyze import TrendAnalyze
from dto.response import *
from data.redis.redis_client import redis_client

download_chart = download_chart()

async def get_trend(day : str):
    day = get_next_thursday(date=datetime.strptime(day, "%Y-%m-%d"))
    cached_data = await redis_client.get("day:" + day)

    if cached_data:
        print("트렌드 캐시 히트")
        cached_data = json.loads(cached_data)
        tracks = [Track(**t) for t in cached_data['tracks']]
        genres = [GenreStat(**g) for g in cached_data['genreStat']]
        genre_distribution = cached_data['genre_distribution']
        return TrendResponse(tracks=tracks, genreStat=genres, genre_distribution=genre_distribution)
    print("트렌드 캐시 미스")
    download_chart.crawl_one(day)
    print("download 완료")

    analyzer = TrendAnalyze(day=day)

    genre_distribution = await analyzer.analyze_metadata()
    genre_stats_df = analyzer.genre_stats_analysis()
    analyzed_df = analyzer.to_dict()

    print(analyzed_df)
    print(genre_stats_df)

    tracks = [Track(img_url=t['album_image_url'], rank=t['rank'], artist_names=t['artist_names'], track_name=t['track_name'], weeks_on_chart=t['weeks_on_chart'], stream_ratio=t['stream_ratio'], genres=t['genres'], popularity=t['popularity']) for t in analyzed_df]
    genres = [GenreStat(**g) for g in genre_stats_df]
    response = TrendResponse(tracks=tracks, genreStat=genres, genre_distribution=genre_distribution)

    await redis_client.set("day:" + day, response.json())
    return response

def get_next_thursday(date: datetime) -> str:
    weekday = date.weekday()
    days_until_thursday = (3 - weekday + 7) % 7
    thursday = date + timedelta(days=days_until_thursday)
    return thursday.strftime("%Y-%m-%d")
