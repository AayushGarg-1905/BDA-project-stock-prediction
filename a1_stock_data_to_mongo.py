import pandas as pd
import yfinance as yf
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URL"))  
db = client['stock_prediction_regression']
stock_col = db['historical_prices']

tickers = ['AAPL', 'GOOGL', 'MSFT']

def fetch_multiple_stocks(symbols, start_date="2023-01-01", end_date="2025-01-01"):
    all_records = []

    for symbol in symbols:
        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date, end=end_date, interval="1d")

        for index, row in data.iterrows():
            date_str = index.strftime("%Y-%m-%d")

            if stock_col.count_documents({"ticker": symbol, "date": date_str}) == 0:
                all_records.append({
                    "ticker": symbol,
                    "date": date_str,
                    "open": row["Open"],
                    "close": row["Close"],
                    "high": row["High"],
                    "low": row["Low"],
                    "volume": row["Volume"]
                })

    if all_records:
        stock_col.insert_many(all_records)
        print(f"Inserted {len(all_records)} new records for {len(symbols)} stocks.")
    else:
        print("No new stock records to insert.")

if __name__ == "__main__":
    fetch_multiple_stocks(tickers)

# fetch_multiple_stocks(tickers, start_date="2025-01-02", end_date="2025-04-11")
