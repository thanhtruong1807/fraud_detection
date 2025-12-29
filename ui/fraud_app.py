import streamlit as st
import requests

st.set_page_config(
    page_title="Fraud Detection",
    page_icon="🛡️",
    layout="wide",
)

CUSTOM_CSS = """
<style>
/* Center main title and reduce empty space */
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* Subtle card style */
.card {
  border: 1px solid rgba(49, 51, 63, 0.2);
  border-radius: 16px;
  padding: 16px 18px;
  background: rgba(255,255,255,0.02);
}

/* KPI numbers */
.kpi {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
}
.kpi-label {
  font-size: 13px;
  opacity: 0.75;
  margin: 0;
}

/* Small muted text */
.muted { opacity: 0.7; font-size: 12px; }

/* Make buttons nicer */
div.stButton > button {
  border-radius: 12px;
  padding: 0.6rem 1rem;
  font-weight: 600;
}
</style>
"""

#st.title("Credit Card Fraud Detection (Real-time Demo)")


from pathlib import Path
from PIL import Image

LOGO_PATH = Path(__file__).parent / "Logo_UIT.jpg"
logo = Image.open(LOGO_PATH)
st.image(logo, width=120)

st.markdown("## 🛡️ Credit Card Fraud Detection")
st.markdown(
    "<div class='muted'>Real-time scoring demo • Logistic Regression pipeline (OneHotEncoder + StandardScaler)</div>",
    unsafe_allow_html=True,
)
st.divider()

st.sidebar.title("Navigation")
if st.sidebar.button("📊 Admin dashboard", use_container_width=True):
    st.switch_page("pages/admin_dashboard.py")

# st.sidebar.title("Navigation")
# if st.sidebar.button("Go to Admin Dashboard"):
#     st.switch_page("pages/admin_dashboard.py")


# API_URL = "http://127.0.0.1:8000/predict"

# tx_type = st.selectbox("Transaction Type", ["CASH_OUT", "TRANSFER", "PAYMENT", "DEBIT", "CASH_IN"])
# amount = st.number_input("Amount", min_value=0.0, value=1000.0)
# oldbalanceOrg = st.number_input("Old Balance Origin", value=10000.0)
# newbalanceOrig = st.number_input("New Balance Origin", value=9000.0)
# oldbalanceDest = st.number_input("Old Balance Destination", value=0.0)
# newbalanceDest = st.number_input("New Balance Destination", value=0.0)




# if st.button("Predict Fraud"):
#     payload = {
#         "type": tx_type,
#         "amount": float(amount),
#         "oldbalanceOrg": float(oldbalanceOrg),
#         "newbalanceOrig": float(newbalanceOrig),
#         "oldbalanceDest": float(oldbalanceDest),
#         "newbalanceDest": float(newbalanceDest),
#     }

#     try:
#         r = requests.post(API_URL, json=payload, timeout=5)
#         r.raise_for_status()
#         out = r.json()

#         st.subheader(f"Decision: {out['decision']}")
#         st.write(f"Fraud probability: {out['fraud_probability']:.2%}")
#         st.caption(f"Model: {out['model_version']} | latency: {out['latency_ms']} ms")

#         if out["decision"] == "BLOCK":
#             st.error("⚠️ Likely fraud — BLOCK")
#         elif out["decision"] == "REVIEW":
#             st.warning("🟠 Suspicious — REVIEW")
#         else:
#             st.success("✅ Looks normal — ALLOW")

#     except Exception as e:
#         st.error(f"API error: {e}")
#         st.info("Kiểm tra xem API có đang chạy ở http://127.0.0.1:8000 không.")


API_URL = "http://127.0.0.1:8000/predict"

left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.markdown("### Input transaction")
    with st.container(border=True):
        tx_type = st.selectbox("Transaction Type", ["CASH_OUT", "TRANSFER", "PAYMENT", "DEBIT", "CASH_IN"])
        amount = st.number_input("Amount", min_value=0.0, value=1000.0, step=100.0, format="%.2f")

        c1, c2 = st.columns(2)
        with c1:
            oldbalanceOrg = st.number_input("Old Balance (Origin)", value=10000.0, step=100.0, format="%.2f")
            oldbalanceDest = st.number_input("Old Balance (Destination)", value=0.0, step=100.0, format="%.2f")
        with c2:
            newbalanceOrig = st.number_input("New Balance (Origin)", value=9000.0, step=100.0, format="%.2f")
            newbalanceDest = st.number_input("New Balance (Destination)", value=0.0, step=100.0, format="%.2f")

        predict_btn = st.button("Run prediction", type="primary", use_container_width=True)

with right:
    st.markdown("### Result")
    result_placeholder = st.empty()

if predict_btn:
    payload = {
        "type": tx_type,
        "amount": float(amount),
        "oldbalanceOrg": float(oldbalanceOrg),
        "newbalanceOrig": float(newbalanceOrig),
        "oldbalanceDest": float(oldbalanceDest),
        "newbalanceDest": float(newbalanceDest),
    }

    try:
        with st.spinner("Scoring..."):
            r = requests.post(API_URL, json=payload, timeout=8)
            r.raise_for_status()
            out = r.json()

        decision = out["decision"]
        proba = float(out["fraud_probability"])
        latency = out.get("latency_ms", None)
        model_version = out.get("model_version", "unknown")

        with result_placeholder.container():
            # KPI row
            k1, k2, k3 = st.columns(3)
            k1.markdown(f"<div class='card'><p class='kpi'>{decision}</p><p class='kpi-label'>Decision</p></div>", unsafe_allow_html=True)
            k2.markdown(f"<div class='card'><p class='kpi'>{proba:.2%}</p><p class='kpi-label'>Fraud probability</p></div>", unsafe_allow_html=True)
            k3.markdown(f"<div class='card'><p class='kpi'>{latency if latency is not None else '-'} ms</p><p class='kpi-label'>Latency</p></div>", unsafe_allow_html=True)

            st.markdown(
                f"<div class='muted'>Model: <b>{model_version}</b> • API: {API_URL}</div>",
                unsafe_allow_html=True,
            )
            st.divider()

            if decision == "BLOCK":
                st.error("⚠️ High risk — recommend **BLOCK** the transaction.")
            elif decision == "REVIEW":
                st.warning("🟠 Medium risk — recommend **MANUAL REVIEW**.")
            else:
                st.success("✅ Low risk — recommend **ALLOW**.")

            # Show input summary
            st.markdown("#### Input summary")
            st.json(payload)

    except Exception as e:
        with result_placeholder.container():
            st.error(f"API error: {e}")
            st.info("Check API is running: http://127.0.0.1:8000/health")
