from typing import List, Optional

from pydantic import BaseModel

class Track(BaseModel):
    img_url: str
    rank : int
    artist_names : str
    track_name : str
    days_on_chart : int
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
