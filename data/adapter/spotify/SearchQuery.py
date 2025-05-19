from typing import Optional

from pydantic import BaseModel


class SearchQuery(BaseModel):
    """Spotify Adapter에서 search를 하기 위한 클래스이다."""
    track: Optional[str] = None
    album: Optional[str] = None
    artist: Optional[str] = None

    def toString(self):
        query = ""
        if self.track:
            query += f"track:{self.track} "
        if self.album:
            query += f"album:{self.album} "
        if self.artist:
            query += f"artist:{self.artist} "
        return query
