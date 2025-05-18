import pandas as pd
from collections import Counter, defaultdict
from data.adapter.spotify.SpotifyAdapter import SpotifyAdapter
import time
from pathlib import Path
from data.redis.redis_client import redis_client

print("import end")

class TrendAnalyze:
    def __init__(self, day):
        self.day = day
        base_dir = Path(__file__).resolve().parent.parent.parent
        download_dir = base_dir / "data" / "downloaded_spotify_files"
        self.filename = download_dir / f"spotify_kr_daily_{day}.csv"

        self.df = pd.read_csv(self.filename)
        self.spotify = SpotifyAdapter()

    async def analyze_metadata(self):
        genre_counter = Counter()
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

                popularity = track_info.get('popularity', None)
                popularities.append(popularity)

                images = track_info.get('album', {}).get('images', [])
                image_url = images[0]['url'] if images else None
                image_urls.append(image_url)

                artist_id = track_info['artists'][0]['id']

                cached_artist = await redis_client.get("artist:" + artist_id)

                if cached_artist:
                    print("아티스트 캐시 히트")
                    artist_info = cached_artist
                else:
                    artist_info = self.spotify.get_artist(artist_id, show_info=True)
                    await redis_client.set("artist:" + artist_id, artist_info, ex=86400)

                genres = artist_info.get('genres', [])
                genres_list.append(genres)
                genre_counter.update(genres)

            except Exception as e:
                print(f"Error processing {row.uri}: {e}")
                genres_list.append([])
                popularities.append(None)
                image_urls.append(None)
                continue

        self.df['genres'] = genres_list
        self.df['popularity'] = popularities
        self.df['album_image_url'] = image_urls

        dict_genre_counter = dict(genre_counter)
        print("장르 분포:", dict_genre_counter)

        return dict_genre_counter

    def genre_stats_analysis(self):
        if 'genres' not in self.df.columns:
            raise ValueError("genre_analysis()를 먼저 실행하여 self.df['genre']를 채워야 합니다.")

        genre_stats = defaultdict(list)

        for _, row in self.df.iterrows():
            for genre in row['genres']:
                genre_stats[genre].append(row['streams'])

        genre_df = pd.DataFrame([
            {
                'genres': genre,
                'avg_streams': sum(values) / len(values),
                'count': len(values)
            }
            for genre, values in genre_stats.items()
        ])

        genre_df.sort_values(by='avg_streams', ascending=False, inplace=True)
        dict_df = genre_df.to_dict(orient='records')
        print("장르별 평균 스트리밍 수")
        print(dict_df)
        return dict_df

    def print_dataframe(self, size=200):
        print(self.df.head(size))

    def to_dict(self):
        return self.df.to_dict(orient='records')

if __name__ == "__main__":
    analyzer = TrendAnalyze(day="2025-05-12")
    analyzer.print_dataframe()

    genre_distribution = analyzer.analyze_metadata()

    genre_stats_df = analyzer.genre_stats_analysis()
    analyzer.print_dataframe()
