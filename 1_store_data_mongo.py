import pandas as pd
import yfinance as yf
from pymongo import MongoClient
from datetime import datetime


client = MongoClient("mongodb://localhost:27017")  
db = client['stock_prediction']
news_col = db['news_sentiment_gnews']
stock_col = db['historical_prices']


news_df = pd.read_csv('news_sentiment_data_randomized.csv')
news_records = news_df.to_dict(orient='records')
news_col.insert_many(news_records)
print(f" Inserted {len(news_records)} news sentiment records.")

tickers = ['AAPL', 'GOOGL', 'MSFT']

def fetch_multiple_stocks(symbols):
    all_records = []
    
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        data = stock.history(start="2023-01-01", end="2025-01-01", interval="1d")

        for index, row in data.iterrows():
            all_records.append({
                "symbol": symbol,
                "timestamp": index.strftime("%Y-%m-%d %H:%M:%S"),
                "open": row["Open"],
                "close": row["Close"],
                "high": row["High"],
                "low": row["Low"],
                "volume": row["Volume"]
            })


    if all_records:
        stock_col.insert_many(all_records)
        print(f"Inserted {len(all_records)} records for {len(symbols)} stocks.")


fetch_multiple_stocks(tickers)


