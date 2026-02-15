import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from database import AssetPrice

load_dotenv()


st.set_page_config(page_title="Automated Wealth Tracker", layout="wide")

st.title("💰 Wealth Tracker Dashboard")


# 1. Load Data
def load_data():
    # Use Peewee to fetch all records and convert to a list of dictionaries
    query = AssetPrice.select().order_by(AssetPrice.date.desc())
    data = list(query.dicts())
    return pd.DataFrame(data)


df = load_data()

# 2. Sidebar Filter
tickers = df['asset_name'].unique()
selected_ticker = st.sidebar.selectbox("Select Asset", tickers)

# 3. Filtered Data
filtered_df = df[df['asset_name'] == selected_ticker].sort_values('date')

# 4. Visualization
st.subheader(f"Price History: {selected_ticker}")
st.line_chart(filtered_df.set_index('date')['price'])

st.subheader("Raw Data")
st.dataframe(df)
