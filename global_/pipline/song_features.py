import pandas as pd
from global_.adapter.spotify.SearchQuery import SearchQuery
from global_.adapter.spotify.SpotifyAdapter import SpotifyAdapter

class KpopTrendAnalyzer:
    def __init__(self):
        self.spotify = SpotifyAdapter()

    def fetch_tracks_features_by_artist(self, artist_name: str, top_n: int = 10) -> pd.DataFrame:
        search_query = SearchQuery(artist=artist_name)
        artist_result = self.spotify.search(q=search_query, type=["artist"], details=True)
        artist_items = artist_result["artists"]["items"]
        if not artist_items:
            raise ValueError(f"'{artist_name}'라는 아티스트를 찾을 수 없습니다.")
        artist_id = artist_items[0]["id"]

        top_tracks = self.spotify.artist_top_tracks(artist_id, show_info=True)["tracks"][:top_n]
        track_ids = [track["id"] for track in top_tracks]
        track_names = [track["name"] for track in top_tracks]

        print(track_names)

        features = self.spotify.get_audio_features(track_ids, show_info=True)

        df = pd.DataFrame(features)
        df["track_name"] = track_names
        return df

if __name__ == "__main__":
    analyzer = KpopTrendAnalyzer()
    df = analyzer.fetch_tracks_features_by_artist("LE SSERAFIM")
    print(df)
