from typing import Optional, List, Dict

from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from data.adapter.genius.GeniusAdapter import GeniusAdapter
from data.adapter.spotify.SearchQuery import SearchQuery
from data.adapter.spotify.SpotifyAdapter import SpotifyAdapter
from fastapi import HTTPException
from dto.response import *
from collections import defaultdict
import json
import re

print("import strart")
import uvicorn
from fastapi import FastAPI
from router.trend import trend_router
print("import router")
print("start")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(trend_router)


genius = GeniusAdapter()
spotify = SpotifyAdapter()

@app.get("/lyrics/{artist}/{song}", response_model=LyricsResponse)
async def get_lyrics(artist: str, song : str):
    try:
        lyrics = genius.search_song_lyrics_with_artist(artist, song)
        if not lyrics or lyrics.strip() == "":
            raise HTTPException(status_code=404, detail="Lyrics not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Genius API error: {str(e)}")
    return LyricsResponse(artist=artist, song=song, lyrics=lyrics)

@app.get("/artist/info/{artist_name}", response_model=ArtistInfoResponse)
async def get_artist_info(artist_name: str):
    try:
        query = SearchQuery(artist=artist_name)
        search_result = await spotify.search(q=query, limit=1, type=["artist"])
        if not search_result['artists']['items']:
            raise HTTPException(status_code=404, detail="Artist not found")
        artist = search_result['artists']['items'][0]
        artist_id = artist['id']
        genres = artist.get('genres', [])
        followers = artist.get('followers', {}).get('total', 0)
        popularity = artist.get('popularity', 0)
        top_tracks_resp = await spotify.artist_top_tracks(artist_id=artist_id)
        top_tracks_list = []
        for track in top_tracks_resp['tracks']:
            top_tracks_list.append(
                TrackInfo(
                    track_name=track['name'],
                    artist_name=track['artists'][0]['name'],
                    album_name=track['album']['name'],
                    track_id=track['id'],
                    image_url=track['album']['images'][0]['url']
                )
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spotify API error: {str(e)}")
    return ArtistInfoResponse(
        artist_name=artist['name'],
        genres=genres,
        followers=followers,
        popularity=popularity,
        image_url = artist['images'][0]['url'] if artist.get('images') else None,
        top_tracks=top_tracks_list
    )

@app.get("/artist/search/{artist_name}", response_model=SimpleArtistSearchResponse)
async def search_artists(artist_name : str):
    try:
        query = SearchQuery(artist=artist_name)
        search_result = await spotify.search(q=query, limit=20, type=["artist"])
        artists = search_result['artists']['items']
        if not artists:
            raise HTTPException(status_code=404, detail="잘못된 검색입니다.")
        print(artists)
        result_list = sorted([
            SimpleArtistInfo(
                artist_name=artist['name'],
                followers=artist.get('followers', {}).get('total', 0),
                popularity=artist.get('popularity', 0),
                image_url = artist['images'][0]['url'] if artist.get('images') else None
            )
            for artist in artists
        ], key=lambda x: x.popularity, reverse=True)
    except Exception as e:
        print(result_list)
        raise HTTPException(status_code=500, detail=f"Spotify API error: {str(e)}")
    return SimpleArtistSearchResponse(results=result_list)

@app.get("/trend/kpop/top", response_model=KpopResponse, summary="K-pop Top 50")
async def get_kpop_top10():
    playlist_id = "4cRo44TavIHN54w46OqRVc" # 멜론 차트 TOP 100
    try:
        playlist = await spotify.get_playlist(playlist_id, show_info=False)
        tracks = playlist['tracks']['items'][:50]
        top_50 = []
        for item in tracks:
            track = item["track"]
            image_url = track["album"]["images"][0]["url"] if track["album"]["images"] else ""
            top_50.append(KpopTrack(
                name=track["name"],
                artist=track["artists"][0]["name"],
                popularity=track["popularity"],
                image_url=image_url
            ))
        return KpopResponse(playlist_name=playlist["name"], top_50_tracks=top_50)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch K-pop Top 50: {str(e)}")

@app.get("/kpop-subgenres", response_model=Dict[str, int])
async def get_kpop_subgenres():
    try:
        playlist_id = "4cRo44TavIHN54w46OqRVc" # 2025년 BEST 플레이리스트
        playlist = await spotify.get_playlist(playlist_id)

        artist_ids = list({
            item["track"]["artists"][0]["id"]
            for item in playlist["tracks"]["items"][:51]
            if item.get("track") and item["track"].get("artists")
        })

        genre_count = defaultdict(int)
        for artist_id in artist_ids:
            artist = await spotify.get_artist(artist_id)
            for genre in artist.get("genres", []):
                genre = genre.lower()

                if genre:
                    genre_count[genre] += 1

        return json.loads(json.dumps(dict(genre_count), ensure_ascii=False))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")


if __name__ == "__main__":
    print("run uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=3030)
