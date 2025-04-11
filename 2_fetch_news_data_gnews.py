import requests
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GNEWS_API_KEY")

stocks = {
    "AAPL": "Apple stock",
    "GOOGL": "Google stock",
    "MSFT": "Microsoft stock"
}

analyzer = SentimentIntensityAnalyzer()
all_results = []

def generate_monthly_ranges(start_date, end_date):
    ranges = []
    current = start_date
    while current < end_date:
        next_month = (current.replace(day=1) + timedelta(days=32)).replace(day=1)
        ranges.append((current.strftime("%Y-%m-%d"), next_month.strftime("%Y-%m-%d")))
        current = next_month
    return ranges

start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 1, 1)
monthly_ranges = generate_monthly_ranges(start_date, end_date)

for ticker, query in stocks.items():
    print(f"\n Fetching news for {ticker}...")
    for from_date, to_date in monthly_ranges:
        print(f"  → {from_date} to {to_date}")
        # print("from date is ",from_date, " ", to_date)
        from_iso = f"{from_date}T00:00:00Z"
        to_iso = f"{to_date}T00:00:00Z"
        url = f"https://gnews.io/api/v4/search?q={query}&from={from_iso}&to={to_iso}&lang=en&max=100&token={API_KEY}"
        try:
            response = requests.get(url)
            data = response.json()
            articles = data.get('articles', [])
            # print("single article is ",articles)
            # break
            for article in articles:
                title = article['title']
                published_at = article['publishedAt'][:10]
                sentiment = analyzer.polarity_scores(title)
                label = 'positive' if sentiment['compound'] >= 0.05 else 'negative' if sentiment['compound'] <= -0.05 else 'neutral'
                all_results.append([ticker, published_at, article['source']['name'], title, sentiment['compound'], label])

        except Exception as e:
            print(f" Error during {from_date} → {to_date}: {e}")

df = pd.DataFrame(all_results, columns=['ticker', 'date', 'source', 'headline', 'vader_score', 'vader_label'])
df.to_csv('news_sentiment_gnews_full.csv', index=False)
print("\n Monthly sentiment data saved as 'news_sentiment_gnews_full.csv'")