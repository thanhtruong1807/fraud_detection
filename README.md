# Fraud Detection - Real-time Demo

Mô tả ngắn: dự án demo đánh giá rủi ro giao dịch (fraud scoring) với backend FastAPI và giao diện Streamlit.

**Yêu cầu**
- Python 3.8+ (Windows)
- (Tùy chọn) Redis nếu dùng consumer/producer

**Cài đặt (PowerShell)**
1. Mở PowerShell và chuyển vào thư mục project:

```
cd E:\Master\subject\bigdata\final_project
```

2. Tạo và kích hoạt virtualenv (project dùng `.venv`):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Nếu dùng `cmd.exe`:

```
.venv\Scripts\activate
```

3. Cài dependencies (nếu không có `requirements.txt`):

```
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" streamlit pandas joblib scikit-learn pydantic pillow requests redis
```

**Chạy Redis (tùy chọn)**
- Dùng Docker (khuyến nghị):

```
docker run -p 6379:6379 --name redis -d redis
```

Hoặc cài Redis trên máy/WSL theo hướng dẫn chính thức nếu muốn.

**Chạy toàn bộ (tự động)**
- File `run_all.bat` đã có sẵn để khởi `API`, `UI`, `consumer` và `producer`. Chỉ cần:

```
.\run_all.bat
```

File này sẽ:
- Kích hoạt `.venv`
- Chạy `uvicorn service.api:app --host 127.0.0.1 --port 8000 --reload`
- Chạy `streamlit run ui\fraud_app.py`
- Chạy `python -m service.consumer_redis` và `python tools\producer_redis.py`

**Chạy thủ công (từng thành phần)**
- Backend (API):

```
uvicorn service.api:app --host 127.0.0.1 --port 8000 --reload
```

- Frontend (Streamlit UI):

```
streamlit run ui\fraud_app.py
```

- Redis consumer:

```
python -m service.consumer_redis
```

- Redis producer:

```
python tools\producer_redis.py
```

**Kiểm tra nhanh**
- Health API: http://127.0.0.1:8000/health (trả về `status: ok` khi API đang chạy)
- Streamlit mặc định: http://localhost:8501

**Các file và đường dẫn quan trọng**
- Model: `model/best_fraud_model.pkl` (đã tồn tại trong repo)
- API: `service/api.py`
- UI: `ui/fraud_app.py`
- Batch chạy nhanh: `run_all.bat`

**Ghi chú / Troubleshooting**
- Nếu PowerShell chặn kích hoạt script, chạy (chỉ cho session hiện tại):

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

- Nếu bạn không muốn dùng Redis, chỉ cần chạy `API` và `UI` như phần "Chạy thủ công".
- Nếu gặp lỗi import, kiểm tra đã kích hoạt `.venv` và đã `pip install` các gói cần thiết.

