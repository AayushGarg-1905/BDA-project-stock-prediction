import pandas as pd

df = pd.read_csv("news_sentiment_gnews_full.csv")

def convert_date_format(col):
    return col.apply(lambda x: '-'.join(x.split('-')[::-1]))

df['date'] = convert_date_format(df['date'])

df.to_csv('news_sentiment_gnews_full_v2.csv', index=False)
print(df)