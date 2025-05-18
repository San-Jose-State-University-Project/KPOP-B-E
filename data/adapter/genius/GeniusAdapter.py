import lyricsgenius
import os
import re
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

class GeniusAdapter:
    def __init__(self):
        token = os.getenv("GENIUS_ACCESS_TOKEN")
        self.genius = lyricsgenius.Genius(token)

    def search_artist(self, artist : str, max_songs : int = 3, sort : str = "title", show_info : bool = False):
        """아티스트를 조회할 수 있다."""
        artist = self.genius.search_artist(artist, max_songs, sort, include_features=True)
        if show_info:
            pprint(artist)
        return artist

    def search_song(self, song : str, show_info : bool = False):
        """노래를 조회할 수 있다."""
        search_result = self.genius.search_song(song)
        if show_info:
            pprint(search_result)
        return search_result

    def search_album(self, album : str, show_info : bool = False):
        """앨범을 조회할 수 있다."""
        search_result = self.genius.search_album(album)
        if show_info:
            pprint(search_result)
        return search_result

    def search_song_lyrics_with_artist(self, artist: str, song: str, show_info: bool = False):
        """아티스트명과 곡 이름으로 가사를 조회할 수 있습니다."""
        search_artist = self.search_artist(artist, show_info)
        search_song = search_artist.song(song)
        lyrics = search_song.lyrics
        cleaned_lyrics = self.clean_lyrics(lyrics)


        if show_info:
            pprint(cleaned_lyrics)
        return cleaned_lyrics

    def search_song_lyrics(self, song: str, show_info : bool = False):
        """곡 이름으로 가사 검색"""
        song = self.search_song(song, show_info)
        lyrics = song.lyrics
        cleaned_lyrics = self.clean_lyrics(lyrics)
        if show_info:
            pprint(cleaned_lyrics)
        return cleaned_lyrics

    def clean_lyrics(self, lyrics: str) -> str:
        """
        가사 앞의 메타 정보 및 [Chorus], [Verse 1] 등의 구간 라벨 제거
        """
        lines = lyrics.strip().split("\n")

        # 1. 처음에 붙은 Contributor, 제목 등 제거
        while lines and (
                "contributor" in lines[0].lower()
                or "lyrics" in lines[0].lower()
                or "[" in lines[0] and "]" in lines[0]
                or lines[0].strip() == ""
        ):
            lines.pop(0)

        cleaned = "\n".join(lines)

        # 2. [Chorus], [Verse 1], [Bridge], ... 제거
        cleaned = re.sub(r"\[.*?\]", "", cleaned)

        # 3. 빈 줄 정리
        cleaned = re.sub(r"\n{2,}", "\n\n", cleaned).strip()

        return cleaned
if __name__ == "__main__":
    genius = GeniusAdapter()
    genius.search_song_lyrics_with_artist("bol4", song="여행", show_info=True)

