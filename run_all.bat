
@echo off
cd /d E:\Master\subject\bigdata\final_project

call .venv\Scripts\activate

start "API" cmd /k uvicorn service.api:app --host 127.0.0.1 --port 8000 --reload
start "UI" cmd /k streamlit run ui\fraud_app.py
start "REDIS_CONSUMER" cmd /k python -m service.consumer_redis
start "REDIS_PRODUCER" cmd /k python tools\producer_redis.py
