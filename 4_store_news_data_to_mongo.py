import pandas as pd
import yfinance as yf
from pymongo import MongoClient
from datetime import datetime


client = MongoClient("mongodb://localhost:27017")  
db = client['stock_prediction_regression']
news_col = db['news_sentiment_gnews']

news_df = pd.read_csv('news_sentiment_gnews_full_v2.csv')
news_records = news_df.to_dict(orient='records')
news_col.insert_many(news_records)
print(f" Inserted {len(news_records)} news sentiment records.")