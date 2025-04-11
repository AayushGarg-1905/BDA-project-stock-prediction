import pandas as pd
import yfinance as yf
from pymongo import MongoClient
from datetime import datetime


client = MongoClient("mongodb://localhost:27017")  
db = client['stock_prediction_regression']

stock_col = db['historical_prices']

tickers = ['AAPL', 'GOOGL', 'MSFT']

def fetch_multiple_stocks(symbols):
    all_records = []
    
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        data = stock.history(start="2023-01-01", end="2025-01-01", interval="1d")

        for index, row in data.iterrows():
            all_records.append({
                "ticker": symbol,
                "date": index.strftime("%Y-%m-%d"),
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


