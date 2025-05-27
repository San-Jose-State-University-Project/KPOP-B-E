from typing import List, Optional

from pydantic import BaseModel

class Track(BaseModel):
    img_url: str
    rank : int
    artist_names : str
    track_name : str
    weeks_on_chart : int
    stream_ratio: float
    genres : Optional[List[str]]
    popularity : int

class GenreStat(BaseModel):
    genres : str
    avg_streams : float
    count : int

class TrendResponse(BaseModel):
    tracks: List[Track]
    genreStat : List[GenreStat]
    genre_distribution : dict[str, int]


class LyricsResponse(BaseModel):
    artist: str
    song: str
    lyrics: str

class TrackInfo(BaseModel):
    track_name: str
    artist_name: str
    album_name: Optional[str] = None
    track_id: Optional[str] = None
    image_url: Optional[str] = None

class ArtistInfoResponse(BaseModel):
    artist_name: str
    genres: Optional[List[str]] = []
    followers: Optional[int] = 0
    popularity: Optional[int] = 0
    top_tracks: List[TrackInfo] = []
    image_url : Optional[str] = None

class SimpleArtistInfo(BaseModel):
    artist_name: str
    followers: int
    popularity: int
    image_url : Optional[str] = None

class SimpleArtistSearchResponse(BaseModel):
    results: List[SimpleArtistInfo]

class SongWithEmotion(BaseModel):
    title: str
    emotion: str

    def to_dict(self):
        return {
            "title": self.title,
            "emotion": self.emotion,
        }

class KpopTrack(BaseModel):
    name: str
    artist: str
    popularity: int
    image_url: str

class KpopResponse(BaseModel):
    playlist_name: str
    top_50_tracks: List[KpopTrack]