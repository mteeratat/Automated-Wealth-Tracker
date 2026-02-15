from database import init_db, AssetPrice
import yfinance as yf
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
import time
import requests

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def send_telegram_alert(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.warning("Telegram credentials missing. Skipping alert.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")


def track_asset():
    init_db()

    today = datetime.now().date()
    watchlist = os.getenv("TICKERS").split(",")
    summary = ""

    for ticker in watchlist:
        sign = "$"
        currency = "USD"
        if ".BK" in ticker:
            sign = "฿"
            currency = "THB"
        isFetchSuccess = False
        isDbSuccess = False
        isCreate = False
        close = None

        for attempt in range(3):
            try:
                info = yf.Ticker(ticker).info
                close = info.get("currentPrice")
                isFetchSuccess = True
                break
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1}: Failed to fetch data for {ticker}: {e}"
                )
                time.sleep(2)
                continue

        if isFetchSuccess:
            for attempt in range(3):
                try:
                    obj, isCreate = AssetPrice.get_or_create(
                        date=today,
                        asset_name=ticker,
                        defaults={
                            "price": close,
                            "currency": currency,
                        },
                    )
                    isDbSuccess = True
                    break
                except Exception as e:
                    logger.error(
                        f"Attempt {attempt + 1}: Database failed for {ticker}: {e}"
                    )
                    time.sleep(2)
                    continue

        if isFetchSuccess:
            if isDbSuccess:
                if isCreate:
                    logger.info(f"✅ Saved {ticker}: {sign}{close:.2f}")
                    summary += f"✅ {ticker}: {sign}{close:.2f}\n"
                else:
                    logger.info(f"ℹ️ {ticker} already tracked for today. Skipping.")
                    summary += f"ℹ️ {ticker}: Already tracked\n"
            else:
                logger.error(f"❌ Database FAILED for {ticker}")
                summary += f"❌ {ticker}: DB Failed\n"
        else:
            logger.error(f"❌ Fetch FAILED for {ticker}")
            summary += f"❌ {ticker}: Fetch Failed\n"

    if summary:
        full_msg = (
            f"💰 Daily Stocks Price for {today.strftime('%d/%m/%Y')}:\n\n{summary}"
        )
        send_telegram_alert(full_msg)


if __name__ == "__main__":
    track_asset()
