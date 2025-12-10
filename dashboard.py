import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AlphaQuant Dashboard", layout="wide")
st.title("📈 AI-Powered Stock Ranker")

market = st.sidebar.selectbox("Select Market", ["IN", "US"])

@st.cache_data(ttl=0)
def load_data(market):
    try:
        # Try loading from root first
        df = pd.read_csv(f"{market}_rankings.csv")
        return df
    except:
        return pd.DataFrame()

df = load_data(market)

if not df.empty:
    # --- SAFE COLUMN MAPPING ---
    # We check what columns actually exist to prevent KeyErrors
    cols = df.columns.tolist()
    
    # score_col = 'Alpha_Score' if 'Alpha_Score' in cols else 'Final_Score'
    score_col = next((c for c in ['Alpha_Score', 'Final_Score', 'ML_Confidence'] if c in cols), None)
    
    if score_col:
        top_stock = df.iloc[0]
        col1, col2 = st.columns([1, 2])
        col1.metric("🏆 Top Pick", top_stock['Ticker'])
        col2.metric("Confidence Score", f"{top_stock[score_col]:.1f}")
        
        st.subheader(f"Top 10 Picks ({market})")
        st.dataframe(df.head(10).style.background_gradient(subset=[score_col], cmap='Greens'))
    else:
        st.error("Data loaded, but score column is missing. Check CSV format.")
        st.write("Columns found:", cols)
else:
    st.warning(f"No data found for {market}. Waiting for GitHub Action to run...")