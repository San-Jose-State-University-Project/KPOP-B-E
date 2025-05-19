import pandas as pd
from collections import Counter, defaultdict
from data.adapter.spotify.SpotifyAdapter import SpotifyAdapter
import time
from pathlib import Path
print("import end")

class TrendAnalyze:
    def __init__(self, day):
        self.day = day
        base_dir = Path(__file__).resolve().parent.parent.parent
        download_dir = base_dir / "data" / "downloaded_spotify_files"
        self.filename = download_dir / f"spotify_kr_daily_{day}.csv"

        self.df = pd.read_csv(self.filename)
        self.spotify = SpotifyAdapter()

    def analyze_metadata(self):
        genre_counter = Counter()
        artist_cache = {}
        genres_list = []
        popularities = []
        image_urls = []

        total_streams = self.df['streams'].sum()
        self.df['stream_ratio'] = self.df['streams'] / total_streams
        print(f"[{self.day}] 총 스트리밍 수: {total_streams:,}")
        print(self.df[['streams', 'stream_ratio']].head())

        for row in self.df.itertuples(index=False):
            try:
                time.sleep(0.5)
                track_info = self.spotify.get_track(str(row.uri), show_info=True)

                # 🎧 인기도
                popularity = track_info.get('popularity', None)
                popularities.append(popularity)

                # 🖼️ 앨범 이미지 URL
                images = track_info.get('album', {}).get('images', [])
                image_url = images[0]['url'] if images else None
                image_urls.append(image_url)

                # 🎼 장르 (아티스트 기반)
                artist_id = track_info['artists'][0]['id']
                if artist_id in artist_cache:
                    artist_info = artist_cache[artist_id]
                else:
                    artist_info = self.spotify.get_artist(artist_id, show_info=True)
                    artist_cache[artist_id] = artist_info

                genres = artist_info.get('genres', [])
                genres_list.append(genres)
                genre_counter.update(genres)

            except Exception as e:
                print(f"Error processing {row.uri}: {e}")
                genres_list.append([])
                popularities.append(None)
                image_urls.append(None)
                continue

        self.df['genre'] = genres_list
        self.df['popularity'] = popularities
        self.df['album_image_url'] = image_urls

        print("장르 분포:", dict(genre_counter))

        return dict(genre_counter)

    def genre_stats_analysis(self):
        if 'genre' not in self.df.columns:
            raise ValueError("genre_analysis()를 먼저 실행하여 self.df['genre']를 채워야 합니다.")

        genre_stats = defaultdict(list)

        for _, row in self.df.iterrows():
            for genre in row['genre']:
                genre_stats[genre].append(row['streams'])

        genre_df = pd.DataFrame([
            {
                'genre': genre,
                'avg_streams': sum(values) / len(values),
                'count': len(values)
            }
            for genre, values in genre_stats.items()
        ])

        genre_df.sort_values(by='avg_streams', ascending=False, inplace=True)
        dict_df = genre_df.to_dict(orient='records')
        print("장르별 평균 스트리밍 수")
        print(genre_df)
        return dict_df

    def print_dataframe(self, size=200):
        print(self.df.head(size))

    def to_dict(self):
        return self.df.to_dict(orient='records')

if __name__ == "__main__":
    analyzer = TrendAnalyze(day="2025-05-12")
    analyzer.print_dataframe()

    analyzer.analyze_metadata()

    genre_stats_df = analyzer.genre_stats_analysis()
    analyzer.print_dataframe()
