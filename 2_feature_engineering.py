import pandas as pd
import yfinance as yf
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")  
db = client['stock_prediction']
news_col = db['news_sentiment_gnews']
stock_col = db['historical_prices']

cursor = stock_col.find({})
data = list(cursor)


df = pd.DataFrame(data)

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['open'] = df['open'].astype(float)
df['close'] = df['close'].astype(float)
df['high'] = df['high'].astype(float)
df['low'] = df['low'].astype(float)
df['volume'] = df['volume'].astype(int)


df.sort_values(by=['symbol', 'timestamp'], inplace=True)

df.dropna(inplace=True)

print(df.head())
