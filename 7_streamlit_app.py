import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import yfinance as yf
import datetime
from pymongo import MongoClient
import joblib

client = MongoClient("mongodb://localhost:27017")
db = client["stock_prediction_regression"]
collection = db["merged_stock_gnews"]

model = joblib.load("xgb_stock_model.pkl")  


st.title("📈 Stock Movement Prediction App")

st.sidebar.header("Prediction Settings")
ticker = st.sidebar.selectbox("Select Stock Ticker", options=collection.distinct("ticker"))
predict_date = st.sidebar.date_input("Prediction Date", datetime.date.today())
predict_button = st.sidebar.button("🔮 Predict")

def generate_features(ticker, date):
    date = pd.to_datetime(date)
    date = date.strftime('%Y-%m-%d')
    data = pd.DataFrame(list(collection.find({"ticker": ticker, "date": {"$lte": date}})))

    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values("date")

    group = data.copy()
    group['prev_close'] = group['close'].shift(1)
    group['return'] = group['close'].pct_change()
    group['ma_3'] = group['close'].rolling(3).mean()
    group['ma_7'] = group['close'].rolling(7).mean()
    group['diff_ma_3'] = group['close'] - group['ma_3']
    group['diff_ma_7'] = group['close'] - group['ma_7']
    group['volatility_3'] = group['return'].rolling(3).std()
    group['volatility_7'] = group['return'].rolling(7).std()
    group['prev_sentiment'] = group['avg_vader_score'].shift(1)
    group['prev_news_count'] = group['news_count'].shift(1)
    group['vader_roll_3'] = group['avg_vader_score'].rolling(3).mean()
    group['news_roll_3'] = group['news_count'].rolling(3).sum()
    group['sentiment_x_news'] = group['avg_vader_score'] * group['news_count']

    group.dropna(inplace=True)

    if group.empty:
        return None, "Not enough historical data for feature generation."

    latest = group.iloc[-1]
    X = latest[[
        'close', 'avg_vader_score', 'news_count', 'prev_sentiment', 'prev_news_count',
        'vader_roll_3', 'news_roll_3', 'sentiment_x_news', 'return',
        'ma_3', 'ma_7', 'diff_ma_3', 'diff_ma_7', 'volatility_3', 'volatility_7'
    ]].values.reshape(1, -1)
    
    close_price = latest['close']
    return X, close_price


# Prediction logic
if predict_button:
    X, close_price = generate_features(ticker, predict_date)
    if X is None:
        st.warning(close_price)  # this contains the error message
    else:
        predicted_log_return = model.predict(X)[0]
        predicted_price = close_price * np.exp(predicted_log_return)

        # Signal generation
        threshold = 0.01  # ~1% log return
        signal = "HOLD"
        if predicted_log_return > threshold:
            signal = "BUY"
        elif predicted_log_return < -threshold:
            signal = "SELL"

        # Display Results
        st.subheader(f"📊 Prediction for {ticker} on {predict_date.strftime('%Y-%m-%d')}")
        st.write(f"Current Price: **${close_price:.2f}**")
        st.write(f"Predicted Future Price (3 days ahead): **${predicted_price:.2f}**")
        st.write(f"Predicted Log Return: **{predicted_log_return:.5f}**")
        st.success(f"Recommended Action: **{signal}**")
