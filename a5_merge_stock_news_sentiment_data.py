from pymongo import MongoClient
from collections import defaultdict
from dotenv import load_dotenv
import os

load_dotenv()

def merge_stock_and_news_data(
    mongo_uri=os.getenv("MONGO_URL"),
    db_name="stock_prediction_regression",
    stock_collection="historical_prices",
    news_collection="news_sentiment_gnews",
    merged_collection="merged_stock_gnews"
):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    stock_col = db[stock_collection]
    news_col = db[news_collection]
    merged_col = db[merged_collection]

    news_cursor = news_col.find({})
    news_grouped = defaultdict(lambda: {"total_score": 0, "count": 0})

    for doc in news_cursor:
        key = (doc["ticker"], doc["date"])
        news_grouped[key]["total_score"] += doc["vader_score"]
        news_grouped[key]["count"] += 1

    stock_cursor = stock_col.find({})
    count = 0

    for stock_doc in stock_cursor:
        ticker = stock_doc["ticker"]
        date = stock_doc["date"]
        key = (ticker, date)
        news_info = news_grouped.get(key, {"total_score": 0, "count": 0})

        merged_doc = {
            "ticker": ticker,
            "date": date,
            "open": stock_doc["open"],
            "high": stock_doc["high"],
            "low": stock_doc["low"],
            "close": stock_doc["close"],
            "volume": stock_doc["volume"],
            "avg_vader_score": round(news_info["total_score"] / news_info["count"], 4) if news_info["count"] > 0 else 0,
            "news_count": news_info["count"]
        }

        merged_col.update_one(
            {"ticker": ticker, "date": date},
            {"$set": merged_doc},
            upsert=True
        )
        count += 1

    print(f"Merged and upserted {count} records.")


if __name__ == "__main__":
    merge_stock_and_news_data()
