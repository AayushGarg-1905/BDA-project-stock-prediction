from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["stock_prediction_regression"]
stock_col = db["historical_prices"]
news_col = db["news_sentiment_gnews"]
merged_col = db["merged_stock_gnews"]

news_cursor = news_col.find({})
news_grouped = defaultdict(lambda: {"total_score": 0, "count": 0})

for doc in news_cursor:
    key = (doc["ticker"], doc["date"])
    news_grouped[key]["total_score"] += doc["vader_score"]
    news_grouped[key]["count"] += 1


stock_cursor = stock_col.find({})
merged_docs = []

for stock_doc in stock_cursor:
    ticker = stock_doc["ticker"]
    date = stock_doc["date"]

    key = (ticker, date)
    news_info = news_grouped.get(key, {"total_score": 0, "count": 0})

    merged_docs.append({
        "ticker": ticker,
        "date": date,
        "open": stock_doc["open"],
        "high": stock_doc["high"],
        "low": stock_doc["low"],
        "close": stock_doc["close"],
        "volume": stock_doc["volume"],
        "avg_vader_score": round(news_info["total_score"] / news_info["count"], 4) if news_info["count"] > 0 else 0,
        "news_count": news_info["count"]
    })


if merged_docs:
    merged_col.delete_many({})  
    merged_col.insert_many(merged_docs)
    print(f" Merged and inserted {len(merged_docs)} records.")
else:
    print(" No records to merge.")