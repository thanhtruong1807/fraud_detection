from fastapi import FastAPI
from service.schemas import Txn
import pandas as pd
import joblib
import time, uuid
from pathlib import Path
import json
from datetime import datetime
from service.settings import MODEL_VERSION, TH_BLOCK, TH_REVIEW



app = FastAPI(title="Fraud Scoring Service")

MODEL_PATH = Path(__file__).resolve().parents[1] / "model" / "best_fraud_model.pkl"
model = joblib.load(MODEL_PATH)

LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "predictions.jsonl"


def decide(p: float) -> str:
    if p >= TH_BLOCK:
        return "BLOCK"
    if p >= TH_REVIEW:
        return "REVIEW"
    return "ALLOW"

@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION}

@app.post("/predict")
def predict(txn: Txn):
    t0 = time.time()
    request_id = str(uuid.uuid4())

    df = pd.DataFrame([txn.model_dump()])
    proba = float(model.predict_proba(df)[:, 1][0])
    decision = decide(proba)

    latency_ms = int((time.time() - t0) * 1000)
    
    log_row = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "model_version": MODEL_VERSION,
        "input": txn.model_dump(),
        "fraud_probability": proba,
        "decision": decision,
        "latency_ms": latency_ms,
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_row, ensure_ascii=False) + "\n")

    
    return {
        "request_id": request_id,
        "model_version": MODEL_VERSION,
        "fraud_probability": proba,
        "decision": decision,
        "thresholds": {"review": TH_REVIEW, "block": TH_BLOCK},
        "latency_ms": latency_ms,
    }

@app.get("/model-info")
def model_info():
    return {
        "model_version": MODEL_VERSION,
        "thresholds": {"review": TH_REVIEW, "block": TH_BLOCK},
        "features": ["type","amount","oldbalanceOrg","newbalanceOrig","oldbalanceDest","newbalanceDest"]
    }