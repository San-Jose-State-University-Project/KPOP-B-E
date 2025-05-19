from typing import Optional, List

from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from data.adapter.genius.GeniusAdapter import GeniusAdapter
from data.adapter.spotify.SearchQuery import SearchQuery
from data.adapter.spotify.SpotifyAdapter import SpotifyAdapter
from fastapi import HTTPException
from dto.response import *

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
def get_lyrics(artist: str, song : str):
    try:
        lyrics = genius.search_song_lyrics_with_artist(artist, song)
        if not lyrics or lyrics.strip() == "":
            raise HTTPException(status_code=404, detail="Lyrics not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Genius API error: {str(e)}")
    return LyricsResponse(artist=artist, song=song, lyrics=lyrics)

@app.get("/artist/info/{artist_name}", response_model=ArtistInfoResponse)
def get_artist_info(artist_name: str):
    try:
        query = SearchQuery(artist=artist_name)
        search_result = spotify.search(q=query, limit=1, type=["artist"])
        if not search_result['artists']['items']:
            raise HTTPException(status_code=404, detail="Artist not found")
        artist = search_result['artists']['items'][0]
        artist_id = artist['id']
        genres = artist.get('genres', [])
        followers = artist.get('followers', {}).get('total', 0)
        popularity = artist.get('popularity', 0)
        top_tracks_resp = spotify.artist_top_tracks(artist_id=artist_id)
        top_tracks_list = []
        for track in top_tracks_resp['tracks']:
            top_tracks_list.append(
                TrackInfo(
                    track_name=track['name'],
                    artist_name=track['artists'][0]['name'],
                    album_name=track['album']['name'],
                    track_id=track['id']
                )
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spotify API error: {str(e)}")
    return ArtistInfoResponse(
        artist_name=artist['name'],
        genres=genres,
        followers=followers,
        popularity=popularity,
        top_tracks=top_tracks_list
    )

@app.get("/artist/search/{artist_name}", response_model=SimpleArtistSearchResponse)
def search_artists(artist_name : str):
    try:
        query = SearchQuery(artist=artist_name)
        search_result = spotify.search(q=query, limit=20, type=["artist"])
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

if __name__ == "__main__":
    print("run uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=3030)
