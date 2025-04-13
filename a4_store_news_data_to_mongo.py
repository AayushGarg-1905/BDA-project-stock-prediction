import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def insert_news_sentiment_to_mongo(csv_path: str, mongo_uri = os.getenv("MONGO_URL"),
                                   db_name: str = "stock_prediction_regression",
                                   collection_name: str = "news_sentiment_gnews"):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    news_col = db[collection_name]

    news_df = pd.read_csv(csv_path)
    news_records = news_df.to_dict(orient='records')

    inserted_count = 0
    for record in news_records:
        query = {
            "ticker": record["ticker"],
            "date": record["date"],
            "headline": record["headline"]
        }

        if not news_col.find_one(query):
            news_col.insert_one(record)
            inserted_count += 1

    print(f"Inserted {inserted_count} new unique news sentiment records into '{collection_name}'.")


if __name__ == "__main__":
    insert_news_sentiment_to_mongo("news_sentiment_gnews_full_v2.csv")