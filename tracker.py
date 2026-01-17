from database import init_db, AssetPrice
import yfinance as yf
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def track_asset():
    init_db()

    watchlist = os.getenv("TICKERS").split(",")

    for ticker in watchlist:
        info = yf.Ticker(ticker).info
        close = info.get('currentPrice')

        obj, created = AssetPrice.get_or_create(
            date=datetime.date.today(),
            asset_name=ticker,
            defaults={
                'price':close,
            }
        )
        if created:
            print(f"✅ Saved {ticker}: ${close}")
        else:
            print(f"ℹ️ {ticker} already tracked for today. Skipping.")

if __name__ == "__main__":
    track_asset()
