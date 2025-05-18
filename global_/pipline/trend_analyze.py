import pandas as pd
from collections import Counter, defaultdict
from global_.adapter.spotify.SpotifyAdapter import SpotifyAdapter
import time
print("import end")


class TrendAnalyze:
    def __init__(self, day):
        self.day = day
        self.filename = f"../downloaded_spotify_files/spotify_kr_daily_{day}.csv"
        self.df = pd.read_csv(self.filename)
        self.spotify = SpotifyAdapter()

    def trend_analyze(self):
        total_streams = self.df['streams'].sum()
        self.df['stream_ratio'] = self.df['streams'] / total_streams
        print(f"[{self.day}] 총 스트리밍 수: {total_streams:,}")
        print(self.df[['streams', 'stream_ratio']].head())

    def genre_analysis(self):
        genre_counter = Counter()
        artist_cache = {}
        genres_list = []

        for row in self.df.itertuples(index=False):
            try:
                time.sleep(0.3)
                track_info = self.spotify.get_track(str(row.uri), show_info=True)
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
                genres_list.append([])  # 실패 시 빈 리스트라도 추가
                continue

        self.df['genre'] = genres_list
        genre_dict = dict(genre_counter)
        print(genre_dict)

        return genre_dict

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
                'avg_streams': sum(values) / len(values),  # ✅ x[0] → x
                'count': len(values)
            }
            for genre, values in genre_stats.items()
        ])

        genre_df.sort_values(by='avg_streams', ascending=False, inplace=True)
        print("장르별 평균 스트리밍 수")
        print(genre_df)

        return genre_df

    def print_dataframe(self, size=200):
        print(self.df.head(size))

    def to_pickle(self):
        return self.df.to_pickle()

    def to_dict(self):
        return self.df.to_dict()

if __name__ == "__main__":
    analyzer = TrendAnalyze(day="2025-05-08")
    analyzer.print_dataframe()

    analyzer.trend_analyze()
    analyzer.genre_analysis()

    genre_stats_df = analyzer.genre_stats_analysis()
    analyzer.print_dataframe()
