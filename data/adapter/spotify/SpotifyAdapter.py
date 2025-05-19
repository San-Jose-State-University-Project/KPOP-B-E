from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotipy
import os
from pprint import pprint
from typing import List
from data.adapter.spotify.SearchQuery import SearchQuery

load_dotenv()

class SpotifyAdapter:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        client_credentials_manager = SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        # auth_manager = SpotifyOAuth(
        #     client_id=self.client_id,
        #     client_secret=self.client_secret,
        #     redirect_uri=redirect_uri,
        #     scope="user-read-private playlist-read-private playlist-read-collaborative",
        # )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        print(self.sp.auth_manager.get_access_token())

    def get_artist(self, artist_id : str, show_info : bool = False, details : bool = False):
        """아티스트의 정보를 조회할 수 있다."""
        artist = self.sp.artist(artist_id)
        # pprint(artist)
        if show_info:
            print(f"이름 : {artist['name']}")
            print(f"장르 : {artist['genres']},")
            print(f"팔로워 수 : {artist['followers']['total']},")
            print(f"인기도 : {artist['popularity']}")
        self.__show_details(artist, details=details)
        return artist

    def get_track(self, track_id : str, show_info : bool = False, details : bool = False):
        """트랙의 정보를 조회 할 수 있다."""
        track = self.sp.track(track_id)
        # pprint(track)
        if show_info:
            print(f"가수 : {track['artists'][0]['name']}")
            print(f'노래명 : {track["name"]}')
            print(f'href : {track["href"]}')
            print(f'인기도 : {track["popularity"]}')
        self.__show_details(track, details=details)

        return track

    def get_playlist(self, playlist_id : str, country="KR", show_info : bool = False, details : bool = False):
        """플레이리스트 정보를 조회할 수 있다."""
        playlist = self.sp.playlist(playlist_id, market=country)

        if show_info:
            print(f"플레이리스트 이름 : {playlist['name']}")
            print(f"플레이리스트 설명 : {playlist['description']}")
            print(f"팔로워 수 : {playlist['followers']['total']}")
            print(f"href : {playlist['href']}")
            print("트랙 리스트 정보 : ")
            for tracks in playlist['tracks']['items']:
                track = tracks['track']
                print(f"    가수 : {track['artists'][0]['name']}")
                print(f'    노래명 : {track["name"]}')
                print(f'    href : {track["href"]}')
                print(f'    인기도 : {track["popularity"]}')
                print("-" * 30)

        self.__show_details(playlist, details=details)
        return playlist

    def get_album(self, album_id : str, market="KR", show_info : bool = False, details : bool = False):
        """앨범 정보를 가져올 수 있다."""
        album = self.sp.album(album_id)
        if show_info:
            print(f"앨범 이름: {album['name']}")
            print(f"가수 : {album['artists'][0]['name']}")
            print(f"인기도 : {album['popularity']}")
            print(f"총 트랙 수 : {album['total_tracks']}")
            print(f"앨범 유형 : {album['album_type']}")
            print("트랙 리스트 정보 : ")
            for track in album['tracks']['items']:
                print(f"    가수 : {track['artists'][0]['name']}")
                print(f'    노래명 : {track["name"]}')
                print(f'    href : {track["href"]}')
                print("-" * 30)

        self.__show_details(album, details=details)
        return album

    def search(self, q : SearchQuery, limit=10, offset=0, type : List[str] = "track", country="KR",  details : bool = False):
        """spotify에서 검색할 수 있다.
        q는 다음과 같은 형태로 올 수 있다.
        SearchQuery 객체가 들어와야한다.
        모든 필드가 있어야 하는 것은 아니나, 한 가지 이상은 있어야 할 것이다.

        type은 다음과 같은 형태로 올 수 있다.
        type=["album", "track"] <-- 이런식으로 리스트 형식으로 넣어주면 된다.
        올 수 있는 목록으로는 album, playlist, track, artist가 있다.
        """
        query = q.toString()

        if isinstance(type, List):
            type = ",".join(t.strip() for t in type if t in ["album", "playlist", "track", "artist"])
        result = self.sp.search(q=query, limit=limit, offset=offset, type=type, market=country)

        self.__show_details(result, details=details)
        return result

    def artist_top_tracks(self, artist_id : str, show_info : bool = False, details : bool = False):
        """아티스트의 인기 많은 곡들을 조회할 수 있다."""
        tracks = self.sp.artist_top_tracks(artist_id=artist_id, country="KR")
        if show_info:
            for track in tracks["tracks"]:
                print(f"트랙 이름 : {track['name']}")
                print(f"인기도 : ", track['popularity'])
                print(f"앨범 이름 : {track['album']['name']}")
                print(f"앨범 트랙 수 : {track['album']['total_tracks']}")

        self.__show_details(tracks, details=details)
        return tracks

    def get_album_tracks(self, album_id: str, show_info : bool = False):
        """앨범의 모든 트랙을 가져올 수 있다."""
        album = self.sp.album(album_id)
        tracks_name = [track["name"] for track in album["tracks"]["items"]]
        if show_info:
            for name in tracks_name:
                print(name)
        return tracks_name

    def get_all_albums_by_artist(self, artist_id: str, country="KR", show_info: bool = False, details: bool = False):
        """아티스트의 모든 앨범을 조회할 수 있다."""
        albums = []
        offset = 0
        while True:
            response = self.sp.artist_albums(artist_id, country=country, limit=50, offset=offset)
            albums.extend(response["items"])
            if response["next"] is None:
                break
            offset += 50

        if show_info:
            for album in albums:
                print(f"앨범 이름: {album['name']}")
                print(f"앨범 ID: {album['id']}")
                print(f"발매일: {album['release_date']}")
                print(f"앨범 유형: {album['album_type']}")
                print("-" * 30)

        self.__show_details(albums, details=details)
        return albums

    def __show_details(self, json, details : bool = False):
        """json을 보기 편하게 만들어주는 메서드이다."""
        if details:
            pprint(json)

spotify_adapter = SpotifyAdapter()

if __name__ == "__main__":
    spotify = SpotifyAdapter()
    #
    # # https://open.spotify.com/artist/1SsVqqC31h54Hg08g7uQhM
    # artist_id = "1SsVqqC31h54Hg08g7uQhM"
    # spotify.get_artist(artist_id)
    # spotify.artist_top_tracks(artist_id=artist_id, show_info=True)
    #
    # # https://open.spotify.com/track/7tI8dRuH2Yc6RuoTjxo4dU
    # track_id = "7tI8dRuH2Yc6RuoTjxo4dU"
    # spotify.get_track(track_id)
    #
    # # https://open.spotify.com/playlist/7KUBkg0P6QTJtJaySQKw4C
    # playlist_id = "7KUBkg0P6QTJtJaySQKw4C"
    # spotify.get_playlist(playlist_id, show_info=True)
    #
    # # https://open.spotify.com/album/7hFjISvuzhZauC3EK66GuG
    # album_id = "7hFjISvuzhZauC3EK66GuG"
    # spotify.get_album(album_id, show_info=True)
    #

    # "album:SLOMO track:SAHARA artist:yanghongwon"
    query = SearchQuery(artist="yanghongwon")
    type = ["artist"]
    spotify.search(q=query, type=type, details=True)
    #
    # spotify.get_all_albums_by_artist(artist_id=artist_id, show_info=True)