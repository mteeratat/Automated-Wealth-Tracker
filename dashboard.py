import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from database import init_db, fetch_asset_prices

# 1. INITIALIZATION
# Load environment variables to ensure we check for Supabase SDK keys
load_dotenv()

# Set up the visual configuration of the dashboard
st.set_page_config(page_title="Automated Wealth Tracker", layout="wide")

st.title("💰 Wealth Tracker Dashboard")


# 2. DATA ACQUISITION
def load_data():
    """
    Fetches the latest data from our unified database layer.
    The dashboard doesn't need to know IF we are using Supabase or SQLite;
    it just calls this function and gets results back!
    """
    init_db()
    data = fetch_asset_prices()

    if not data:
        # Return an empty DataFrame with the correct column structure if no data exists
        return pd.DataFrame(columns=["date", "asset_name", "price", "currency"])

    # Convert the list of dictionaries into a Pandas DataFrame for easy manipulation
    df = pd.DataFrame(data)
    return df


# Main execution flow starts here
df = load_data()

# 3. INTERACTIVE UI LOGIC
if not df.empty:
    # Sidebar: Creates a dropdown containing all unique tickers found in the data
    tickers = df["asset_name"].unique()
    selected_ticker = st.sidebar.selectbox("Select Asset to Visualize", tickers)

    # Filtering: Get only the rows for the selected asset and sort them by date (past -> present)
    # This ensures the line graph flows correctly.
    filtered_df = df[df["asset_name"] == selected_ticker].sort_values("date")

    # 4. VISUALIZATION LAYER
    # Show a clean line chart of the price trends
    st.subheader(f"📈 Price History: {selected_ticker}")
    st.line_chart(filtered_df.set_index("date")["price"])

    # Show the raw data table for users who want to see exact numbers
    st.subheader("📋 Raw Data Feed")
    st.dataframe(df.sort_values("date", ascending=False))
else:
    # Elegant error handling for new users with no data yet
    st.warning(
        "📭 No data found in the database yet. Run the 'tracker.py' script to fetch some prices!"
    )
