import streamlit as st
import pandas as pd
import sqlite3
from streamlit_autorefresh import st_autorefresh

# ========================
# 🚀 Dashboard Setup
# ========================
st.set_page_config(page_title="🕋 Hajj Tweet Monitor", layout="wide")
st.title("🕌 Hajj & Haramain Tweet Sentiment Dashboard")



# ✅ Manual refresh button
if st.button("🔁 Refresh Now"):
    st.experimental_rerun()

# ========================
# 📦 Load tweet database
# ========================
conn = sqlite3.connect("hajj_tweets.db")

try:
    df = pd.read_sql_query("SELECT * FROM tweets ORDER BY created_at DESC", conn)
except Exception as e:
    st.error(f"❌ Could not load database: {e}")
    st.stop()

# ========================
# 📊 Sidebar Filters
# ========================
st.sidebar.header("🔎 Filters")

preset = st.sidebar.radio("🌐 Language Filter", ["All", "Arabic Only", "English Only"], index=0)
sentiments = st.sidebar.multiselect("❤️ Sentiment", df["sentiment"].unique(), default=list(df["sentiment"].unique()))

lang_filter = {
    "All": df["lang"].unique().tolist(),
    "Arabic Only": ["ar"],
    "English Only": ["en"]
}.get(preset, df["lang"].unique().tolist())

# ========================
# 🧼 Apply filters
# ========================
filtered = df[(df["sentiment"].isin(sentiments)) & (df["lang"].isin(lang_filter))]

# ========================
# 🔔 New Tweet Notification
# ========================
if "last_tweet_count" not in st.session_state:
    st.session_state.last_tweet_count = 0

new_count = len(filtered)
if new_count > st.session_state.last_tweet_count:
    st.success(f"🆕 {new_count - st.session_state.last_tweet_count} new tweet(s) found!")
    st.balloons()
    st.session_state.last_tweet_count = new_count
else:
    st.info(f"📦 Showing {new_count} tweet(s)")

# ========================
# 📊 Charts + Table
# ========================
if not filtered.empty:
    st.subheader("📊 Sentiment Distribution")
    st.bar_chart(filtered["sentiment"].value_counts())

    st.subheader("📋 Tweets Table")
    st.dataframe(filtered[["created_at", "lang", "sentiment", "text"]], use_container_width=True)
else:
    st.warning("📭 No tweets match your filters.")
