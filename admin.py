import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="🛠 Admin Control Panel", layout="wide")

# 🔐 Protect this page
st.title("🛡️ Admin Mode: Delete Tweets")
admin_password = st.text_input("Enter Admin Password", type="password")
if admin_password != "444":
    st.warning("Access denied. Admin password required.")
    st.stop()

# ✅ Connect to DB
conn = sqlite3.connect("hajj_tweets.db")
cursor = conn.cursor()
df = pd.read_sql_query("SELECT * FROM tweets ORDER BY created_at DESC", conn)

# ✅ Select tweets to delete
st.write("Select irrelevant tweets to delete:")
to_delete = st.multiselect("Choose tweet IDs to delete", df["id"].tolist(), format_func=lambda x: df[df["id"] == x]["text"].values[0][:100])

if st.button("🗑 Delete Selected Tweets"):
    for tweet_id in to_delete:
        cursor.execute("DELETE FROM tweets WHERE id = ?", (tweet_id,))
    conn.commit()
    st.success(f"✅ Deleted {len(to_delete)} tweet(s)!")
    st.experimental_rerun()

# Optional: show preview
st.write("📋 Preview of all tweets:")
st.dataframe(df[["id", "created_at", "lang", "sentiment", "text"]], use_container_width=True)
