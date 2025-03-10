import pandas as pd


def create_events(btc_data, news):

    # Format date
    news['date'] = pd.to_datetime(news['date'])
    news = news.sort_values(by='date')

    # Drop events with nan in text column
    events = news.dropna(subset=['text'])

    #% Join events with stock data based on date use closes time reference
    events = pd.merge(events, btc_data, how='left', left_on='date', right_on='timestamp')

    # Create a new column with the next day's close price
    events['next_t_close'] = events['close'].shift(-100)

    # Calculate close price rolling stats 7 ts, 30 ts, 90 ts
    events['close_7'] = events['close'].rolling(7).mean()
    events['close_30'] = events['close'].rolling(30).mean()
    events['close_90'] = events['close'].rolling(90).mean()

    # Drop first 100 rows
    events = events.dropna(subset=['next_t_close'])
    events = events.dropna(subset=['close_90'])

    # if next_day_close is lower than close, then 1 else 0
    events['target'] = events.apply(lambda x: "Long" if x['next_t_close'] > x['close'] else "short", axis=1)

    # calculate the difference between next_day_close and close
    events['diff_perc'] = ((events['next_t_close'] / events['close']) - 1) * 100

    return events