## Deployed Link: https://bda-project-stock-prediction-citwxnyy6i8deb2ngbd8uw.streamlit.app/

### Steps to run the code on local
- For training from scratch
1. clone the repository
2. Run: pip install -r requirements.txt
3. create a .env file and set GNEWS_API_KEY=your_actual_key and MONGO_URL=your_mongo_connection_string(you can either use mongodb atlas or compass)

- For prediction on new data
1. Run: streamlit run 7_streamlit_app.py
