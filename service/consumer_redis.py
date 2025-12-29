import json
import time
from pathlib import Path
from datetime import datetime

import pandas as pd
import joblib
import redis

from service.redis_settings import (
    REDIS_HOST, REDIS_PORT,
    TX_STREAM, DECISION_STREAM,
    CONSUMER_GROUP, CONSUMER_NAME
)

# Load model (pipeline)
MODEL_PATH = Path(__file__).resolve().parents[1] / "model" / "fraud_detection_model.pkl"
model = joblib.load(MODEL_PATH)

# Thresholds (đồng bộ với API của bạn nếu muốn)
TH_BLOCK = 0.75
TH_REVIEW = 0.35
MODEL_VERSION = "v1.0.0"

LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "predictions.jsonl"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def decide(p: float) -> str:
    if p >= TH_BLOCK:
        return "BLOCK"
    if p >= TH_REVIEW:
        return "REVIEW"
    return "ALLOW"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Create consumer group if not exists
try:
    r.xgroup_create(TX_STREAM, CONSUMER_GROUP, id="0", mkstream=True)
except redis.exceptions.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise

print(f"Consumer ready. Stream={TX_STREAM}, Group={CONSUMER_GROUP}, Name={CONSUMER_NAME}")

while True:
    # Read new messages
    resp = r.xreadgroup(
        groupname=CONSUMER_GROUP,
        consumername=CONSUMER_NAME,
        streams={TX_STREAM: ">"},
        count=50,
        block=2000,
    )

    if not resp:
        continue

    for stream_name, messages in resp:
        for msg_id, fields in messages:
            t0 = time.time()

            # parse fields -> dataframe
            txn = {
                "type": fields.get("type", ""),
                "amount": float(fields.get("amount", "0")),
                "oldbalanceOrg": float(fields.get("oldbalanceOrg", "0")),
                "newbalanceOrig": float(fields.get("newbalanceOrig", "0")),
                "oldbalanceDest": float(fields.get("oldbalanceDest", "0")),
                "newbalanceDest": float(fields.get("newbalanceDest", "0")),
            }

            df = pd.DataFrame([txn])
            proba = float(model.predict_proba(df)[:, 1][0])
            decision = decide(proba)
            latency_ms = int((time.time() - t0) * 1000)

            out = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "tx_id": msg_id,
                "model_version": MODEL_VERSION,
                "fraud_probability": proba,
                "decision": decision,
                "latency_ms": latency_ms,
                "input": txn,
            }

            # Write to decision stream
            r.xadd(DECISION_STREAM, {
                "tx_id": msg_id,
                "decision": decision,
                "fraud_probability": str(proba),
                "latency_ms": str(latency_ms),
                "model_version": MODEL_VERSION,
                "payload": json.dumps(txn),
                "ts": out["ts"],
            })

            # Write JSONL log for your admin dashboard (reuse existing)
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(out, ensure_ascii=False) + "\n")

            # Ack message
            r.xack(TX_STREAM, CONSUMER_GROUP, msg_id)

            print("DEC >", msg_id, decision, f"{proba:.3f}", f"{latency_ms}ms")
