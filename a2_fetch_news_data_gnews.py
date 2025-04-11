
stocks = {
    "AAPL": "Apple stock",
    "GOOGL": "Google stock",
    "MSFT": "Microsoft stock"
}
import requests
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GNEWS_API_KEY")

analyzer = SentimentIntensityAnalyzer()

def generate_monthly_ranges(start_date, end_date):
    ranges = []
    current = start_date
    while current < end_date:
        next_month = (current.replace(day=1) + timedelta(days=32)).replace(day=1)
        ranges.append((current.strftime("%Y-%m-%d"), next_month.strftime("%Y-%m-%d")))
        current = next_month
    return ranges

def fetch_gnews_sentiment(start_date: datetime, end_date: datetime, stocks: dict, output_csv_path: str):
    all_results = []
    monthly_ranges = generate_monthly_ranges(start_date, end_date)

    for ticker, query in stocks.items():
        print(f"\nFetching news for {ticker}...")
        for from_date, to_date in monthly_ranges:
            print(f"  → {from_date} to {to_date}")
            from_iso = f"{from_date}T00:00:00Z"
            to_iso = f"{to_date}T00:00:00Z"
            url = f"https://gnews.io/api/v4/search?q={query}&from={from_iso}&to={to_iso}&lang=en&max=100&token={API_KEY}"

            try:
                response = requests.get(url)
                data = response.json()
                articles = data.get('articles', [])
                for article in articles:
                    title = article['title']
                    published_at = article['publishedAt'][:10]
                    sentiment = analyzer.polarity_scores(title)
                    label = 'positive' if sentiment['compound'] >= 0.05 else 'negative' if sentiment['compound'] <= -0.05 else 'neutral'
                    all_results.append([ticker, published_at, article['source']['name'], title, sentiment['compound'], label])

            except Exception as e:
                print(f" Error during {from_date} → {to_date}: {e}")

    df = pd.DataFrame(all_results, columns=['ticker', 'date', 'source', 'headline', 'vader_score', 'vader_label'])
    df.to_csv(output_csv_path, index=False)
    print(f"\nMonthly sentiment data saved to: {output_csv_path}")

if __name__ == "__main__":
    fetch_gnews_sentiment(
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2025, 1, 1),
    stocks=stocks,
    output_csv_path='news_sentiment_gnews_full_v2.csv'
)