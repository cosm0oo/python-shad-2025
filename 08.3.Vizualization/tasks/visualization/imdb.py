import pandas as pd


def wins_correlation() -> str:
    df = pd.read_csv('imdb.csv', on_bad_lines='skip')
    numeric_df = df.select_dtypes(include=['number'])
    correlations = numeric_df.corr()['nrOfWins'].drop('nrOfWins')
    result = correlations.abs().idxmax()
    return str(result)


def imdb_rating_by_time() -> tuple[str, int]:
    df = pd.read_csv('imdb.csv', on_bad_lines='skip')
    df['decade'] = (df['year'] // 10) * 10
    decade_ratings = df.groupby('decade')['imdbRating'].mean()
    trend = 'ascending' if decade_ratings.iloc[-1] > decade_ratings.iloc[0] else 'descending'
    best_decade = int(decade_ratings.idxmax())  # type: ignore
    return trend, best_decade


def genre_ratings() -> tuple[str, str]:
    df = pd.read_csv('imdb.csv', on_bad_lines='skip')
    genres = ['Action', 'Adult', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime',
              'Documentary', 'Drama', 'Family', 'Fantasy', 'FilmNoir', 'GameShow', 'History',
              'Horror', 'Music', 'Musical', 'Mystery', 'News', 'RealityTV', 'Romance', 'SciFi',
              'Short', 'Sport', 'TalkShow', 'Thriller', 'War', 'Western']
    genre_counts = {genre: df[df[genre] == 1].shape[0] for genre in genres}
    top_genres = sorted(genre_counts.items(), key=lambda x: (-x[1], x[0]))[:10]
    top_genre_names = [g[0] for g in top_genres]
    results = []
    for genre in top_genre_names:
        genre_data = df[df[genre] == 1]
        if len(genre_data) > 0:
            ratings = genre_data['imdbRating']
            median = float(ratings.median())  # type: ignore
            q75 = float(ratings.quantile(0.75))  # type: ignore
            q25 = float(ratings.quantile(0.25))  # type: ignore
            iqr = q75 - q25
            results.append((genre, median, iqr))
    results_sorted_by_median = sorted(results, key=lambda x: (-x[1], x[0]))
    results_sorted_by_iqr = sorted(results, key=lambda x: (-x[2], x[0]))
    return results_sorted_by_median[0][0], results_sorted_by_iqr[0][0]


def number_of_words_mode() -> int:
    df = pd.read_csv('imdb.csv', on_bad_lines='skip')
    word_counts = df['wordsInTitle'].str.split().str.len()
    mode_value = word_counts.mode()[0]
    return int(float(mode_value))


def short_movie_year() -> int:
    df = pd.read_csv('imdb.csv', on_bad_lines='skip')
    df = df[df['year'] >= 1920]
    df['decade'] = (df['year'] // 10) * 10
    df['is_short'] = df['duration'] < 3600
    decade_short_share = df.groupby('decade')['is_short'].mean()
    best_decade = int(decade_short_share.idxmax())  # type: ignore
    return best_decade


def movie_reviews() -> str:
    df = pd.read_csv('imdb.csv', on_bad_lines='skip')
    genres = ['Action', 'Adult', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime',
              'Documentary', 'Drama', 'Family', 'Fantasy', 'FilmNoir', 'GameShow', 'History',
              'Horror', 'Music', 'Musical', 'Mystery', 'News', 'RealityTV', 'Romance', 'SciFi',
              'Short', 'Sport', 'TalkShow', 'Thriller', 'War', 'Western']
    max_reviews = -1
    max_genre = ''
    for genre in genres:
        total_reviews = df[df[genre] == 1]['nrOfUserReviews'].sum()
        if total_reviews > max_reviews:
            max_reviews = total_reviews
            max_genre = genre
    return max_genre
