import streamlit as st
import pandas as pd
import sqlite3
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="🕋 Hajj Dashboard", layout="wide")

# Optional password screen (if you want it here too)
password = st.sidebar.text_input("Enter password to view", type="password")
if password != "444":
    st.warning("Please enter the correct password to access the dashboard.")
    st.stop()

st.title("🕌 Hajj & Haramain Tweet Sentiment Dashboard")

st_autorefresh(interval=30000, key="auto_refresh")

conn = sqlite3.connect("hajj_tweets.db")
df = pd.read_sql_query("SELECT * FROM tweets ORDER BY created_at DESC", conn)

# Filters
preset = st.sidebar.radio("🌐 Language", ["All", "Arabic Only", "English Only"])
sentiments = st.sidebar.multiselect("❤️ Sentiment", df["sentiment"].unique(), default=list(df["sentiment"].unique()))

lang_filter = {
    "All": df["lang"].unique().tolist(),
    "Arabic Only": ["ar"],
    "English Only": ["en"]
}.get(preset, df["lang"].unique().tolist())

filtered = df[(df["sentiment"].isin(sentiments)) & (df["lang"].isin(lang_filter))]

st.subheader("📊 Sentiment Distribution")
st.bar_chart(filtered["sentiment"].value_counts())

st.subheader("📋 Tweets")
st.dataframe(filtered[["created_at", "lang", "sentiment", "text"]], use_container_width=True)
