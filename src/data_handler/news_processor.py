import pandas as pd

def process_news(sample=1000):
    # Load raw data
    news = pd.read_csv('data/news/raw/news_btc.csv', nrows=sample)

    # Sample data
    news = news.head(sample)

    # cols to keep
    cols = ['published_date', 'title', 'summary','clean_url', 'authors']
    news = news[cols]

    # rename cols to more generic
    news.columns = ['date', 'title', 'summary', 'publisher', 'authors']

    # Concat tilte, summary, publisher into a single columns
    news['text'] = 'Title:\n ' + news['title'] + '\n\nContent:\n ' + news['summary'] + '\n\nPublisher & Author:\n ' + news['publisher'] + '\n ' + news['authors']
    news = news.drop(['title', 'summary', 'authors','publisher'], axis=1)

    # Process date so it looks like 2025-01-29 00:00:00 (rounded to hours)
    news['date'] = pd.to_datetime(news['date']).dt.floor('h').dt.strftime('%Y-%m-%d %H:%M:%S')

    # Save processed data
    news.to_csv(f'data/news/processed/news_btc_{sample}.csv', index=False)

    # print results
    print(f'Processed {sample} news articles')

    return news















