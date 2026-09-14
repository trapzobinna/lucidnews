import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Lucid Debug Admin", layout="wide")
st.title("Lucid Admin / Debug View")

DB_PATH = "../backend/lucid.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

st.sidebar.header("Tables")
table = st.sidebar.radio("Select Table", ["articles", "scores", "sources", "user_goals", "briefings"])

try:
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 100", conn)
    st.write(f"### {table.capitalize()} (Latest 100)")
    st.dataframe(df, use_container_width=True)
    
    if table == "scores":
        st.write("### Score Breakdown")
        st.write("Distribution of Credibility and Relevance scores for debugging cutoff weights.")
        st.bar_chart(df[['credibility_score', 'relevance_score']])

except Exception as e:
    st.error(f"Error reading database: {e}")
finally:
    conn.close()
