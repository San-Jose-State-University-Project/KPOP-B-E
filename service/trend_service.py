import json
from datetime import datetime, timedelta

from data.adapter.spotify.SpotifyAdapter import SpotifyAdapter
from data.pipline.emotion_classification_pipline import emotion_pipeline
from data.analyze.download_chart import DownloadChart as download_chart
from data.analyze.trend_analyze import TrendAnalyze
from dto.response import *
from data.redis.redis_client import redis_client
from data.adapter.genius.GeniusAdapter import genius_adapter
from collections import Counter

download_chart = download_chart()
spotipy_adapter = SpotifyAdapter()

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


async def get_emotion_by_artist(artist_name):
    cached_data = await redis_client.get("artist:emotion:" + artist_name)
    if cached_data:
        print(cached_data)
        return cached_data
    emotion_list = []
    artist = await genius_adapter.search_artist(artist_name)

    for song in artist.songs:
        print(song.title)
        try:
            emotion = await emotion_pipeline.classification(song.lyrics)
            song_with_emotion = SongWithEmotion(title=song.title, emotion=emotion)
            print(song_with_emotion)
            dict_song = song_with_emotion.to_dict()
            emotion_list.append(dict_song)
        except Exception as e:
            print(f"Error processing {song.title} : {song.lyrics}")
            print(e)

    print("start")

    emotion_counter = Counter(song['emotion'] for song in emotion_list)

    ordered_emotions = [
        'joy',
        'sadness',
        'surprise',
        'anger',
        'disgust',
        'neutral',
        'fear'
    ]

    result = {emotion: emotion_counter.get(emotion, 0) for emotion in ordered_emotions}

    emotion_dict = {
        "artist_name": artist_name,
        "emotion_list": emotion_list,
        "emotion_count": dict(result)
    }
    await redis_client.set("artist:emotion:" + artist_name, emotion_dict, ex=86400)
    print(emotion_dict)
    return emotion_dict

async def get_emotion_by_song(song_name):
    cached_data = await redis_client.get("song:emotion:" + song_name)
    if cached_data:
        print(cached_data)
        return cached_data
    song = await genius_adapter.search_song(song_name)
    emotion = await emotion_pipeline.classification(song.lyrics)
    song_with_emotion = SongWithEmotion(title=song_name, emotion=emotion)
    dict_song = song_with_emotion.to_dict()

    # requests.get("http://10.150.2.2/api/search", )

    print(type(dict_song))
    await redis_client.set("song:emotion:" + song_name, dict_song, ex=86400)

    print(song_with_emotion)
    return song_with_emotion


async def get_genre_distribution(day):
    cached_data = await redis_client.get(f"genre_distribution:{day}")
    if cached_data:
        print("genre_distribution 캐시 히트")
        return cached_data

    await download_chart.crawl_one(day)
    analyzer = TrendAnalyze(day=day)
    genre_distribution = await analyzer.analyze_metadata()

    await redis_client.set(f"genre_distribution:{day}", json.dumps(genre_distribution), ex=86400)
    print("genre_distribution 캐시 저장 완료")
    return genre_distribution


async def get_chart(day):
    day = get_next_thursday(date=datetime.strptime(day, "%Y-%m-%d"))
    cached_data = await redis_client.get(f"chart:{day}")
    if cached_data:
        print("chart 캐시 히트")
        return json.loads(cached_data)
    await download_chart.crawl_one(day)
    analyzer = TrendAnalyze(day=day)
    dict_chart = analyzer.to_dict()
    for item in dict_chart:
        uri = item['uri']
        track = await spotipy_adapter.get_track(uri)
        item['image_url'] = track['album']['images'][0]['url']

    await redis_client.set(f"chart:{day}", json.dumps(dict_chart), ex=86400)
    print("chart 캐시 저장 완료")
    return dict_chart
