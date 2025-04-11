import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import yfinance as yf
import datetime
from pymongo import MongoClient
import joblib
import os
from a1_stock_data_to_mongo import fetch_multiple_stocks
from a2_fetch_news_data_gnews import fetch_gnews_sentiment
from a3_feature_engineering_news_data import convert_date_format_in_csv
from a4_store_news_data_to_mongo import insert_news_sentiment_to_mongo
from a5_merge_stock_news_sentiment_data import merge_stock_and_news_data
import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["stock_prediction_regression"]
collection = db["merged_stock_gnews"]

model_path = "xgb_stock_model.pkl"
model = joblib.load(model_path)

st.title("Stock Movement Prediction App")

st.sidebar.header("Prediction Settings")
ticker = st.sidebar.selectbox("Select Stock Ticker", options=collection.distinct("ticker"))
predict_date = st.sidebar.date_input("Prediction Date", datetime.date.today())
predict_button = st.sidebar.button("🔮 Predict")

st.sidebar.markdown("---")
st.sidebar.subheader("Model Update")
update_button = st.sidebar.button("Update Model with Latest Data")

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

def update_model():
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    end_date = datetime.datetime.strptime(today, "%Y-%m-%d")
    fetch_multiple_stocks([ticker], start_date="2025-01-02", end_date=today)
    if(ticker=="AAPL"):
        fetch_gnews_sentiment(start_date=datetime.datetime(2025, 1, 1),
    end_date=end_date,stocks={ticker:"Apple stock"},output_csv_path="news_sentiment_latest.csv")
    elif(ticker=="GOOGL"):
        fetch_gnews_sentiment(start_date=datetime.datetime(2025, 1, 1),
    end_date=end_date,stocks={ticker:"Google stock"},output_csv_path="news_sentiment_latest.csv")
    else:
        fetch_gnews_sentiment(start_date=datetime.datetime(2025, 1, 1),
    end_date=end_date,stocks={ticker:"Microsoft stock"},output_csv_path="news_sentiment_latest.csv")
    
    insert_news_sentiment_to_mongo("news_sentiment_latest.csv")
    merge_stock_and_news_data()

    all_data = pd.DataFrame(list(collection.find()))
    all_data['date'] = pd.to_datetime(all_data['date'])
    print("all data is ")
    print(all_data)
    print(all_data.dtypes)

    print(pd.to_datetime("2025-01-01"))
    new_data = all_data[all_data['date'] > pd.to_datetime("2025-01-01")].copy()
    print("new data is ")
    print(new_data)
    if len(new_data)<=0:
        return "No new data available to update the model."

    new_data.sort_values(by=["ticker", "date"], inplace=True)
    new_data['prev_close'] = new_data['close'].shift(1)
    new_data['return'] = new_data['close'].pct_change()
    new_data['ma_3'] = new_data['close'].rolling(3).mean()
    new_data['ma_7'] = new_data['close'].rolling(7).mean()
    new_data['diff_ma_3'] = new_data['close'] - new_data['ma_3']
    new_data['diff_ma_7'] = new_data['close'] - new_data['ma_7']
    new_data['volatility_3'] = new_data['return'].rolling(3).std()
    new_data['volatility_7'] = new_data['return'].rolling(7).std()
    new_data['prev_sentiment'] = new_data['avg_vader_score'].shift(1)
    new_data['prev_news_count'] = new_data['news_count'].shift(1)
    new_data['vader_roll_3'] = new_data['avg_vader_score'].rolling(3).mean()
    new_data['news_roll_3'] = new_data['news_count'].rolling(3).sum()
    new_data['sentiment_x_news'] = new_data['avg_vader_score'] * new_data['news_count']
    new_data['future_close'] = new_data['close'].shift(-3)
    new_data['future_return'] = np.log(new_data['future_close'] / new_data['close'])
    new_data['future_return_smooth'] = new_data['future_return'].rolling(5).mean()
    new_data.dropna(inplace=True)

    if new_data.empty or 'future_return_smooth' not in new_data.columns:
        return "Not enough new data with target value for model update."

    X_new = new_data[[
        'close', 'avg_vader_score', 'news_count', 'prev_sentiment', 'prev_news_count',
        'vader_roll_3', 'news_roll_3', 'sentiment_x_news', 'return',
        'ma_3', 'ma_7', 'diff_ma_3', 'diff_ma_7', 'volatility_3', 'volatility_7'
    ]]
    y_new = new_data['future_return_smooth']

    model.fit(X_new, y_new, xgb_model=model)
    joblib.dump(model, model_path)
    return "Model updated with new data!"

if predict_button:
    X, close_price = generate_features(ticker, predict_date)
    if X is None:
        st.warning(close_price)  
    else:
        predicted_log_return = model.predict(X)[0]
        predicted_price = close_price * np.exp(predicted_log_return)

        threshold = 0.01
        signal = "HOLD"
        if predicted_log_return > threshold:
            signal = "BUY"
        elif predicted_log_return < -threshold:
            signal = "SELL"

        st.subheader(f"Prediction for {ticker} on {predict_date.strftime('%Y-%m-%d')}")
        st.write(f"Current Price: **${close_price:.2f}**")
        st.write(f"Predicted Future Price (3 days ahead): **${predicted_price:.2f}**")
        st.write(f"Predicted Log Return: **{predicted_log_return:.5f}**")
        st.success(f"Recommended Action: **{signal}**")


if update_button:
    status = update_model()
    st.info(status)
