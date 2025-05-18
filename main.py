from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from global_.adapter.genius.GeniusAdapter import GeniusAdapter
from global_.adapter.spotify.SpotifyAdapter import SpotifyAdapter, SearchQuery

app = FastAPI()
genius = GeniusAdapter()
spotify = SpotifyAdapter()

class LyricsRequest(BaseModel):
    artist: str
    song: str

class LyricsResponse(BaseModel):
    artist: str
    song: str
    lyrics: str

class ArtistTracksRequest(BaseModel):
    artist_name: str

class TrackInfo(BaseModel):
    track_name: str
    artist_name: str
    album_name: Optional[str] = None
    track_id: Optional[str] = None

class ArtistInfoResponse(BaseModel):
    artist_name: str
    genres: Optional[List[str]] = []
    followers: Optional[int] = 0
    popularity: Optional[int] = 0
    top_tracks: List[TrackInfo] = []

@app.post("/lyrics", response_model=LyricsResponse)
def get_lyrics(request: LyricsRequest):
    try:
        lyrics = genius.search_song_lyrics_with_artist(request.artist, request.song)
        if not lyrics or lyrics.strip() == "":
            raise HTTPException(status_code=404, detail="Lyrics not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Genius API error: {str(e)}")

    return LyricsResponse(artist=request.artist, song=request.song, lyrics=lyrics)


@app.post("/artist-info", response_model=ArtistInfoResponse)
def get_artist_info(request: ArtistTracksRequest):
    try:
        query = SearchQuery(artist=request.artist_name)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3030, reload=True)
