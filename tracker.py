from database import init_db, AssetPrice
import yfinance as yf
import datetime
import os
from dotenv import load_dotenv
import logging
import time

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def track_asset():
    init_db()

    watchlist = os.getenv("TICKERS").split(",")

    for ticker in watchlist:
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
                        date=datetime.date.today(),
                        asset_name=ticker,
                        defaults={
                            "price": close,
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
                    logger.info(f"✅ Saved {ticker}: ${close}")
                else:
                    logger.info(f"ℹ️ {ticker} already tracked for today. Skipping.")
            else:
                logger.error(f"❌ Database FAILED for {ticker}")
        else:
            logger.error(f"❌ Fetch FAILED for {ticker}")


if __name__ == "__main__":
    track_asset()
