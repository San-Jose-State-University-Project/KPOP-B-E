from typing import List, Optional

from pydantic import BaseModel


class Track(BaseModel):
    img_url: str
    rank : int
    artist_names : str
    track_name : str
    days_on_chart : int
    stream_ratio: int
    genres : Optional[List[str]]
    popularity : int

class GenreStat(BaseModel):
    genre : str
    avg_streams : int
    count : int


class TrendResponse(BaseModel):
    tracks: List[Track]
    total : List[GenreStat]
