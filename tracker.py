from database import init_db, save_asset_price
import yfinance as yf
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
import time
import requests

# 1. Configuration & Initialization
load_dotenv()

# Set up logging for professional observability
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def send_telegram_alert(message):
    """
    Sends a status update or error message to a designated Telegram Chat.
    Uses the Bot API with tokens stored in environment variables.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.warning("Telegram credentials missing. Skipping alert.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        # Send post request to Telegram Bot API
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")


def track_asset():
    """
    The main worker function.
    Fetches stock prices, saves them to the database, and sends a summary alert.
    """
    # Initialize the database (creates table if using SQLite fallback)
    init_db()

    # Get the list of stocks to watch from .env
    watchlist = os.getenv("TICKERS", "").split(",")
    summary = ""
    run_date = datetime.now().date()

    for ticker in watchlist:
        if not ticker:
            continue

        # Define currency and symbols based on the ticker name (.BK = Thailand)
        sign = "$"
        currency = "USD"
        if ".BK" in ticker:
            sign = "฿"
            currency = "THB"

        isFetchSuccess = False
        isDbSuccess = False
        isCreate = False
        close = None
        market_date = None

        # --- STEP 1: FETCH DATA (with RETRY logic) ---
        for attempt in range(3):
            try:
                # SRE TIP: Using history(period='1d') instead of info
                # This gives us the ACTUAL market date for that price!
                t = yf.Ticker(ticker)
                hist = t.history(period="1d")

                if not hist.empty:
                    close = hist["Close"].iloc[-1]
                    # Extract the date from the index (timezone-aware market date)
                    market_date = hist.index[0].date()
                    isFetchSuccess = True
                    break
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1}: Failed to fetch data for {ticker}: {e}"
                )
                time.sleep(2)  # Wait 2 seconds before retrying
                continue

        # --- STEP 2: SAVE TO DATABASE (with RETRY logic) ---
        if isFetchSuccess and market_date:
            for attempt in range(3):
                try:
                    # Save using the ACTUAL market date, not the system clock!
                    isDbSuccess, isCreate = save_asset_price(
                        market_date, ticker, close, currency
                    )
                    break
                except Exception as e:
                    logger.error(
                        f"Attempt {attempt + 1}: Database failed for {ticker}: {e}"
                    )
                    time.sleep(2)  # Wait 2 seconds before retrying
                    continue

        # --- STEP 3: RESULT LOGGING & SUMMARY ---
        if isFetchSuccess:
            if isDbSuccess:
                if isCreate:
                    # New record added
                    logger.info(f"✅ Saved {ticker} [{market_date}]: {sign}{close:.2f}")
                    summary += f"✅ {ticker} ({market_date}): {sign}{close:.2f}\n"
                else:
                    # Idempotency: Record already existed for today
                    logger.info(
                        f"ℹ️ {ticker} already tracked for {market_date}. Skipping."
                    )
                    summary += f"ℹ️ {ticker} ({market_date}): Already tracked\n"
            else:
                logger.error(f"❌ Database FAILED for {ticker}")
                summary += f"❌ {ticker}: DB Failed\n"
        else:
            logger.error(f"❌ Fetch FAILED for {ticker}")
            summary += f"❌ {ticker}: Fetch Failed\n"

    # --- STEP 4: FINAL ALERT ---
    if summary:
        full_msg = (
            f"💰 Wealth Tracker Daily Summary:\n"
            f"Run Time: {run_date.strftime('%d/%m/%Y')}\n\n"
            f"{summary}"
        )
        send_telegram_alert(full_msg)


if __name__ == "__main__":
    # Start the worker
    track_asset()
