# import json
# from pathlib import Path
# from datetime import datetime

# import pandas as pd
# import streamlit as st
# import redis

# def require_admin():
#     # đã login thì bỏ qua
#     if st.session_state.get("admin_ok"):
#         return True

#     st.sidebar.subheader("🔒 Admin Login")
#     pw = st.sidebar.text_input("Password", type="password")

#     if st.sidebar.button("Login", use_container_width=True):
#         if pw == st.secrets.get("ADMIN_PASSWORD", ""):
#             st.session_state["admin_ok"] = True
#             st.success("Login success ✅")
#             st.rerun()
#         else:
#             st.session_state["admin_ok"] = False
#             st.error("Wrong password ❌")

#     st.info("Please login to view admin dashboard.")
#     return False

# if not require_admin():
#     st.stop()


# # st.set_page_config(page_title="Fraud Admin Dashboard", layout="wide")
# # st.title("📊 Fraud Detection - Admin Dashboard")
# st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")
# st.markdown("## 📊 Fraud Detection — Admin Dashboard")
# st.markdown("<div class='muted'>Operational monitoring • decisions, latency, and recent high-risk events</div>", unsafe_allow_html=True)
# st.divider()

# st.sidebar.title("Navigation")
# if st.sidebar.button("🛡️ Fraud app", use_container_width=True):
#     st.switch_page("fraud_app.py")

# if st.sidebar.button("Logout", use_container_width=True):
#     st.session_state["admin_ok"] = False
#     st.rerun()

# LOG_PATH = Path(__file__).resolve().parents[1] / "../logs" / "predictions.jsonl"

# def load_logs(path: Path, max_rows: int = 50000) -> pd.DataFrame:
#     if not path.exists():
#         return pd.DataFrame()

#     rows = []
#     # đọc từ cuối lên để nhanh (file lớn vẫn ổn)
#     with open(path, "r", encoding="utf-8") as f:
#         lines = f.readlines()[-max_rows:]

#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue
#         try:
#             rows.append(json.loads(line))
#         except Exception:
#             pass

#     if not rows:
#         return pd.DataFrame()

#     df = pd.json_normalize(rows)
#     # ts -> datetime
#     if "ts" in df.columns:
#         df["ts"] = pd.to_datetime(df["ts"], errors="coerce", utc=True)
#         df["ts_local"] = df["ts"].dt.tz_convert(None)
#     return df




# with st.sidebar:
#     st.header("⚙️ Controls")
#     auto_refresh = st.checkbox("Auto refresh (2s)", value=True)
#     max_rows = st.slider("Load last N rows", 1000, 50000, 10000, step=1000)
#     decision_filter = st.multiselect(
#         "Filter decisions",
#         options=["ALLOW", "REVIEW", "BLOCK"],
#         default=["ALLOW", "REVIEW", "BLOCK"],
#     )

# df = load_logs(LOG_PATH, max_rows=max_rows)

# if df.empty:
#     st.warning("Chưa có log. Hãy đảm bảo API đang ghi vào logs/predictions.jsonl (Bước 9).")
#     st.stop()

# # filter decisions
# if "decision" in df.columns:
#     df = df[df["decision"].isin(decision_filter)]

# # KPIs
# # c1, c2, c3, c4 = st.columns(4)
# # total = len(df)
# # allow = int((df["decision"] == "ALLOW").sum())
# # review = int((df["decision"] == "REVIEW").sum())
# # block = int((df["decision"] == "BLOCK").sum())

# # c1.metric("Total predictions", f"{total:,}")
# # c2.metric("ALLOW", f"{allow:,}")
# # c3.metric("REVIEW", f"{review:,}")
# # c4.metric("BLOCK", f"{block:,}")
# total = len(df)
# allow = int((df["decision"] == "ALLOW").sum())
# review = int((df["decision"] == "REVIEW").sum())
# block = int((df["decision"] == "BLOCK").sum())

# k1, k2, k3, k4 = st.columns(4, gap="large")
# k1.metric("Total predictions", f"{total:,}")
# k2.metric("ALLOW", f"{allow:,}")
# k3.metric("REVIEW", f"{review:,}")
# k4.metric("BLOCK", f"{block:,}")

# st.subheader("Top risky events (latest logs)")
# cols = [c for c in ["ts_local","fraud_probability","decision","input.type","input.amount","latency_ms"] if c in df.columns]
# st.dataframe(
#     df.sort_values(["fraud_probability","ts_local"], ascending=[False, False])[cols].head(30),
#     use_container_width=True,
#     height=380
# )



# st.divider()

# # Charts
# left, right = st.columns([2, 1])

# with left:
#     st.subheader("Decisions over time (last logs)")
#     # group by minute
#     if "ts_local" in df.columns:
#         tmp = df.dropna(subset=["ts_local"]).copy()
#         tmp["minute"] = tmp["ts_local"].dt.floor("min")
#         pivot = (
#             tmp.groupby(["minute", "decision"])
#                .size()
#                .reset_index(name="count")
#                .pivot(index="minute", columns="decision", values="count")
#                .fillna(0)
#                .sort_index()
#         )
#         st.line_chart(pivot)

#     st.subheader("Latency (ms)")
#     if "latency_ms" in df.columns:
#         st.write(
#             {
#                 "p50": float(df["latency_ms"].quantile(0.50)),
#                 "p95": float(df["latency_ms"].quantile(0.95)),
#                 "p99": float(df["latency_ms"].quantile(0.99)),
#                 "max": int(df["latency_ms"].max()),
#             }
#         )
#         st.line_chart(df["latency_ms"].reset_index(drop=True))

# with right:
#     st.subheader("Top transaction types")
#     if "input.type" in df.columns:
#         st.dataframe(
#             df["input.type"].value_counts().head(10).rename_axis("type").reset_index(name="count"),
#             use_container_width=True,
#         )

#     st.subheader("Highest fraud_probability")
#     if "fraud_probability" in df.columns:
#         cols = [c for c in ["ts_local", "fraud_probability", "decision", "input.type", "input.amount"] if c in df.columns]
#         st.dataframe(
#             df.sort_values("fraud_probability", ascending=False)[cols].head(20),
#             use_container_width=True,
#         )

# st.divider()
# st.subheader("Raw logs (latest 200)")
# st.dataframe(df.sort_values("ts_local", ascending=False).head(200), use_container_width=True)

# if auto_refresh:
#     st.caption("Auto refresh ON (2s).")
#     st.rerun()


import json
import time
import pandas as pd
import streamlit as st
import redis
import sys
from pathlib import Path

# Add project root to PYTHONPATH so Streamlit can import `service`
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../final_project
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from service.redis_settings import (
    REDIS_HOST,
    REDIS_PORT,
    TX_STREAM,
    DECISION_STREAM,
    CONSUMER_GROUP,
)

# -----------------------------
# Page config + small CSS
# -----------------------------
st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")
st.markdown(
    """
<style>
.muted { opacity: 0.7; font-size: 12px; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Auth
# -----------------------------
def require_admin():
    if st.session_state.get("admin_ok"):
        return True

    st.sidebar.subheader("🔒 Admin Login")
    pw = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login", use_container_width=True):
        if pw == st.secrets.get("ADMIN_PASSWORD", ""):
            st.session_state["admin_ok"] = True
            st.success("Login success ✅")
            st.rerun()
        else:
            st.session_state["admin_ok"] = False
            st.error("Wrong password ❌")

    st.info("Please login to view admin dashboard.")
    return False

if not require_admin():
    st.stop()

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("Navigation")
if st.sidebar.button("🛡️ Fraud app", use_container_width=True):
    st.switch_page("fraud_app.py")

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state["admin_ok"] = False
    st.rerun()

with st.sidebar:
    st.header("⚙️ Controls")
    auto_refresh = st.checkbox("Auto refresh (2s)", value=True)
    max_rows = st.slider("Load last N rows", 200, 20000, 2000, step=200)
    decision_filter = st.multiselect(
        "Filter decisions",
        options=["ALLOW", "REVIEW", "BLOCK"],
        default=["ALLOW", "REVIEW", "BLOCK"],
    )

# -----------------------------
# Redis connection
# -----------------------------
rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def load_decisions_from_redis(max_rows: int = 2000) -> pd.DataFrame:
    """
    Load latest decisions from DECISION_STREAM (Redis Streams).
    Newest->oldest via XREVRANGE, then sort to oldest->newest for charts.
    """
    try:
        msgs = rds.xrevrange(DECISION_STREAM, max="+", min="-", count=max_rows)
    except Exception:
        return pd.DataFrame()

    rows = []
    for msg_id, fields in msgs:
        payload = fields.get("payload", "{}")
        try:
            payload_obj = json.loads(payload)
        except Exception:
            payload_obj = {}

        # ts from consumer_redis is ISO string "....Z"
        ts_str = fields.get("ts")

        rows.append(
            {
                "stream_id": msg_id,
                "ts": ts_str,
                "tx_id": fields.get("tx_id"),
                "decision": fields.get("decision"),
                "fraud_probability": float(fields.get("fraud_probability", "nan")),
                "latency_ms": float(fields.get("latency_ms", "nan")),
                "model_version": fields.get("model_version"),
                "input.type": payload_obj.get("type"),
                "input.amount": payload_obj.get("amount"),
                "input.oldbalanceOrg": payload_obj.get("oldbalanceOrg"),
                "input.newbalanceOrig": payload_obj.get("newbalanceOrig"),
                "input.oldbalanceDest": payload_obj.get("oldbalanceDest"),
                "input.newbalanceDest": payload_obj.get("newbalanceDest"),
            }
        )

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # ts -> datetime
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce", utc=True)
    df["ts_local"] = df["ts"].dt.tz_convert(None)

    # oldest -> newest
    df = df.sort_values("ts_local", ascending=True, na_position="last")
    return df

def get_stream_health() -> dict:
    info = {}
    try:
        info["decision_stream_len"] = rds.xlen(DECISION_STREAM)
        info["tx_stream_len"] = rds.xlen(TX_STREAM)

        # Consumer group info
        groups = rds.xinfo_groups(TX_STREAM)
        g = next((x for x in groups if x.get("name") == CONSUMER_GROUP), None)
        info["consumer_group"] = CONSUMER_GROUP
        if g:
            info["pending"] = g.get("pending", 0)
            info["consumers"] = g.get("consumers", 0)
            # lag may exist depending on Redis version
            info["lag"] = g.get("lag", None)
        else:
            info["pending"] = None
            info["consumers"] = None
            info["lag"] = None
    except Exception:
        # redis down / stream not exists
        pass
    return info

# -----------------------------
# Header
# -----------------------------
st.markdown("## 📊 Fraud Detection — Admin Dashboard")
st.markdown(
    "<div class='muted'>Streaming monitoring (Redis Streams) • decisions, latency, high-risk events</div>",
    unsafe_allow_html=True,
)
st.divider()

stream_info = get_stream_health()

m1, m2, m3, m4 = st.columns(4)
m1.metric("decision_stream length", stream_info.get("decision_stream_len", "—"))
m2.metric("tx_stream length", stream_info.get("tx_stream_len", "—"))
m3.metric("pending (group)", stream_info.get("pending", "—"))
m4.metric("consumers", stream_info.get("consumers", "—"))
st.divider()

# -----------------------------
# Load data
# -----------------------------
df = load_decisions_from_redis(max_rows=max_rows)

if df.empty:
    st.warning(
        "No data from Redis decision_stream.\n\n"
        "Check:\n"
        "- Redis server is running\n"
        "- producer_redis.py is producing to tx_stream\n"
        "- consumer_redis.py is consuming and writing to decision_stream"
    )
    st.stop()

# Filter decisions
df = df[df["decision"].isin(decision_filter)]

# KPIs
total = len(df)
allow = int((df["decision"] == "ALLOW").sum())
review = int((df["decision"] == "REVIEW").sum())
block = int((df["decision"] == "BLOCK").sum())

k1, k2, k3, k4 = st.columns(4, gap="large")
k1.metric("Total decisions", f"{total:,}")
k2.metric("ALLOW", f"{allow:,}")
k3.metric("REVIEW", f"{review:,}")
k4.metric("BLOCK", f"{block:,}")

st.divider()

# Top risky
st.subheader("Top risky events (latest)")
cols = [c for c in ["ts_local", "fraud_probability", "decision", "input.type", "input.amount", "latency_ms"] if c in df.columns]
st.dataframe(
    df.sort_values(["fraud_probability", "ts_local"], ascending=[False, False])[cols].head(30),
    use_container_width=True,
    height=360,
)

st.divider()

# Charts
left, right = st.columns([2, 1], gap="large")

with left:
    st.subheader("Decisions over time")
    tmp = df.dropna(subset=["ts_local"]).copy()
    if not tmp.empty:
        tmp["minute"] = tmp["ts_local"].dt.floor("min")
        pivot = (
            tmp.groupby(["minute", "decision"])
            .size()
            .reset_index(name="count")
            .pivot(index="minute", columns="decision", values="count")
            .fillna(0)
            .sort_index()
        )
        st.line_chart(pivot)

    st.subheader("Latency (ms)")
    if "latency_ms" in df.columns:
        st.write(
            {
                "p50": float(df["latency_ms"].quantile(0.50)),
                "p95": float(df["latency_ms"].quantile(0.95)),
                "p99": float(df["latency_ms"].quantile(0.99)),
                "max": float(df["latency_ms"].max()),
            }
        )
        st.line_chart(df["latency_ms"].reset_index(drop=True))

with right:
    st.subheader("Top transaction types")
    if "input.type" in df.columns:
        st.dataframe(
            df["input.type"].value_counts().head(10).rename_axis("type").reset_index(name="count"),
            use_container_width=True,
            height=280,
        )

    st.subheader("Highest fraud_probability")
    cols2 = [c for c in ["ts_local", "fraud_probability", "decision", "input.type", "input.amount"] if c in df.columns]
    st.dataframe(
        df.sort_values(["fraud_probability", "ts_local"], ascending=[False, False])[cols2].head(20),
        use_container_width=True,
        height=280,
    )

st.divider()
st.subheader("Raw stream data (latest 200)")
st.dataframe(df.sort_values("ts_local", ascending=False).head(200), use_container_width=True)

# Auto refresh every ~2s
if auto_refresh:
    time.sleep(2)
    st.rerun()
