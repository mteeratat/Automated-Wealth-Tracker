import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from database import init_db, fetch_asset_prices

load_dotenv()


st.set_page_config(page_title="Automated Wealth Tracker", layout="wide")

st.title("💰 Wealth Tracker Dashboard")


# 1. Load Data
def load_data():
    init_db()
    data = fetch_asset_prices()

    if not data:
        return pd.DataFrame(columns=["date", "asset_name", "price", "currency"])

    df = pd.DataFrame(data)
    return df


df = load_data()

if not df.empty:
    # 2. Sidebar Filter
    tickers = df["asset_name"].unique()
    selected_ticker = st.sidebar.selectbox("Select Asset", tickers)

    # 3. Filtered Data
    filtered_df = df[df["asset_name"] == selected_ticker].sort_values("date")

    # 4. Visualization
    st.subheader(f"Price History: {selected_ticker}")
    st.line_chart(filtered_df.set_index("date")["price"])

    st.subheader("Raw Data")
    st.dataframe(df)
else:
    st.warning(
        "📭 No data found in the database yet. Run the tracker script to fetch some prices!"
    )
