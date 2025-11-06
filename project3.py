# get data
import pandas as pd
import requests
import csv
from io import StringIO

url = "https://raw.githubusercontent.com/yinghaoz1/tmdb-movie-dataset-analysis/master/tmdb-movies.csv"

def download_tmdb_dataset(url):
    try:
        response = requests.get(url,timeout=30)
        response.raise_for_status()

        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)

        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading data: {e}")
        raise SystemExit(e)

    except Exception as e:
        print(f"Error parsing data: {e}")

def save_to_file(data, filename="tmdb_movies.csv"):
    if data is None:
        return
    
    try:
        data.to_csv(filename, index=False)
        print(f"Saved to file: {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")

dataset = download_tmdb_dataset(url)
save_to_file(dataset)


#1. Sắp xếp các bộ phim theo ngày phát hành giảm dần rồi lưu ra một file mới
def convert_release_date(date_str):
    month, day, year = date_str.split('/')
    year = int(year)
    full_year = 1900 + year if year > 25 else 2000 + year
    return f"{full_year}-{month}-{day}"

dataset['release_date'] = dataset['release_date'].apply(convert_release_date)
dataset['release_date'] = pd.to_datetime(dataset['release_date'], format='%Y-%m-%d')
dataset_sorted = dataset.sort_values('release_date', ascending=False)
save_to_file(dataset_sorted, filename="task1_sort_release_date.csv")


#2. Lọc ra các bộ phim có đánh giá trung bình trên 7.5 rồi lưu ra một file mới
dataset_filtered_task2 = dataset[dataset['vote_average']>7.5]
save_to_file(dataset_filtered_task2, filename="task2_filtered_vote_average.csv")


#3. Tìm ra phim nào có doanh thu cao nhất và doanh thu thấp nhất
highest = dataset.loc[dataset['revenue'].idxmax()]
lowest = dataset.loc[dataset['revenue'].idxmin()]
result_task3 = pd.DataFrame({
    'title': [highest['original_title'], lowest['original_title']],
    'revenue': [highest['revenue'], lowest['revenue']]
})
save_to_file(result_task3, filename="task3_highest_lowest_revenue.csv")


#4. Tính tổng doanh thu tất cả các bộ phim
total_revenue = dataset['revenue'].sum()
print(f'Tổng doanh thu của tất cả các bộ phim là: {total_revenue:,.0f} USD')


#5. Top 10 bộ phim đem về lợi nhuận cao nhất
dataset['profit'] = dataset['revenue'] - dataset['budget']
top10_profit = dataset.nlargest(10, 'profit')[['original_title', 'budget', 'revenue', 'profit']]
print(top10_profit)


#6.Đạo diễn nào có nhiều bộ phim nhất và diễn viên nào đóng nhiều phim nhất
#directors
directors = dataset[dataset['director'].notna() & (dataset['director'] != '')]
director_counts = (
    directors.groupby('director')
      .size()
      .reset_index(name='num_movies')
      .sort_values('num_movies', ascending=False)
)
top10_directors = director_counts.head(10)
print(top10_directors.head(1))

#actors
cast_series = dataset['cast'].dropna()
cast_series = cast_series[cast_series != '']
all_actors = cast_series.str.split('|').explode()
actor_counts = (
    all_actors.value_counts()
    .reset_index()
    .rename(columns={'index': 'actor', 0: 'num_movies'})
)
top10_actors = actor_counts.head(10)
print(top10_actors)


#7. Thống kê số lượng phim theo các thể loại. Ví dụ có bao nhiêu phim thuộc thể loại Action, bao nhiêu thuộc thể loại Family, ….
genres_series = dataset['genres'].dropna()
genres_series = genres_series[genres_series != '']
all_genres = genres_series.str.split('|').explode()
genre_counts = (
    all_genres.value_counts()
    .reset_index()
    .rename(columns={'index': 'genre', 0: 'num_movies'})
)
print(genre_counts.head(10))