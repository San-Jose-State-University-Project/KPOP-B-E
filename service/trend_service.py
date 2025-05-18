
from data.pipline.download_chart import DownloadChart as download_chart
from data.pipline.trend_analyze import TrendAnalyze
from dto.response import *

download_chart = download_chart()

def get_trend(day : str):
    download_chart.crawl_one_day(day)

    analyzer = TrendAnalyze(day=day)
    analyzer.analyze_metadata()

    genre_stats_df = analyzer.genre_stats_analysis()
    analyzed_df = analyzer.to_dict()

    print(analyzed_df)
    print(genre_stats_df)

    tracks = [Track(**t) for t in analyzed_df]
    genres = [GenreStat(**g) for g in genre_stats_df]

    response = TrendResponse(tracks, genres)
    return response