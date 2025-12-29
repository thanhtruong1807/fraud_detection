import time
import random
import redis

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from service.redis_settings import REDIS_HOST, REDIS_PORT, TX_STREAM

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

types = ["CASH_OUT", "TRANSFER", "PAYMENT", "DEBIT", "CASH_IN"]

def gen_txn():
    amt = round(random.uniform(1, 200000), 2)
    obo = round(random.uniform(0, 500000), 2)
    nbo = max(0.0, obo - amt)
    obd = round(random.uniform(0, 500000), 2)
    nbd = obd + amt
    return {
        "type": random.choice(types),
        "amount": str(amt),
        "oldbalanceOrg": str(obo),
        "newbalanceOrig": str(nbo),
        "oldbalanceDest": str(obd),
        "newbalanceDest": str(nbd),
        "ts": str(time.time()),
    }

print(f"Producing to Redis Stream: {TX_STREAM}")
while True:
    msg = gen_txn()
    msg_id = r.xadd(TX_STREAM, msg)
    print("TX >", msg_id, msg["type"], msg["amount"])
    time.sleep(0.2)
