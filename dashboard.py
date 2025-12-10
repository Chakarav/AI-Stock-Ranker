import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="AlphaQuant Newsletter", layout="wide")
st.title("📰 Daily Alpha Newsletter Dashboard")

# 2. Sidebar
market = st.sidebar.selectbox("Select Market", ["IN", "US"])

# 3. Load Data
@st.cache_data
def load_data(market):
    try:
        # Load the new rankings with P/E and Sentiment
        df = pd.read_csv(f"{market}_rankings.csv")
        return df
    except:
        return pd.DataFrame()

df = load_data(market)

# 4. KPI Metrics
if not df.empty:
    top_stock = df.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🏆 Top Pick", top_stock['Ticker'])
    col2.metric("📊 Final Score", f"{top_stock['Final_Score']:.1f}/100")
    col3.metric("💰 P/E Ratio", f"{top_stock['PE_Ratio']:.2f}")

    st.markdown("---")

    # 5. The "Newsletter" Table
    st.subheader(f"Top Recommendations for {market}")
    
    # We color the table based on Final Score
    # We use a simple dataframe display to avoid the matplotlib crash for now
    st.dataframe(
        df[['Ticker', 'Final_Score', 'PE_Ratio', 'Sentiment', 'Close']],
        use_container_width=True,
        hide_index=True
    )

    # 6. Analysis Chart
    st.subheader("Factor Analysis")
    # Scatter plot: Value (P/E) vs Score
    fig = px.scatter(
        df, 
        x='PE_Ratio', 
        y='Final_Score', 
        color='Sentiment',
        text='Ticker',
        title="Value vs. Quality vs. Sentiment",
        labels={'PE_Ratio': 'P/E Ratio (Lower is Better)', 'Final_Score': 'Alpha Score'},
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error(f"No data found for {market}. Please upload {market}_rankings.csv to GitHub.")