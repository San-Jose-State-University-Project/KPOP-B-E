import pandas as pd
from global_.adapter.spotify.SpotifyAdapter import SpotifyAdapter
from global_.adapter.spotify.SearchQuery import SearchQuery
spotify = SpotifyAdapter()
df = pd.read_csv("KoreaWeeklyMay2025.csv")

from collections import Counter
import matplotlib.pyplot as plt

genre_counter = Counter()

for row in df.itertuples(index=False):
    uri = row.uri

    try:
        artist_id = spotify.get_track(uri, show_info=True)['artists'][0]['id']
        genres = spotify.get_artist(artist_id, show_info=True)['genres']

        genre_counter.update(genres)
    except Exception as e:
        print(f"Error processing {uri}: {e}")
        continue

# 상위 20개 장르 시각화
top_genres = genre_counter.most_common(20)
genres, counts = zip(*top_genres)

plt.figure(figsize=(12, 6))
plt.barh(genres, counts, color='skyblue')
plt.xlabel('Count')
plt.title('Top 20 Genres in Korean Spotify Top 200')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

