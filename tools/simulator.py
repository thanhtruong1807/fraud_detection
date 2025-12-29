import random, time, requests

HEALTH_URL = "http://127.0.0.1:8000/health"

print("Waiting for API to be ready...")
while True:
    try:
        r = requests.get(HEALTH_URL, timeout=2)
        if r.status_code == 200:
            print("API is ready ✅")
            break
    except Exception:
        pass
    time.sleep(1)

API_URL = "http://127.0.0.1:8000/predict"
types = ["CASH_OUT","TRANSFER","PAYMENT","DEBIT","CASH_IN"]

def gen_txn():
    amt = round(random.uniform(1, 200000), 2)
    obo = round(random.uniform(0, 500000), 2)
    nbo = max(0.0, obo - amt)
    obd = round(random.uniform(0, 500000), 2)
    nbd = obd + amt
    return {
        "type": random.choice(types),
        "amount": amt,
        "oldbalanceOrg": obo,
        "newbalanceOrig": nbo,
        "oldbalanceDest": obd,
        "newbalanceDest": nbd,
    }

while True:
    payload = gen_txn()
    r = requests.post(API_URL, json=payload, timeout=5)
    out = r.json()
    print(out["decision"], f'{out["fraud_probability"]:.3f}', payload["type"], payload["amount"])
    time.sleep(0.2)
