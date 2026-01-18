import yfinance as yf
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/stock/{ticker}")
def get_ticker_info(ticker: str):
    info = yf.Ticker(ticker).info
    if not info.get("symbol"):
        raise HTTPException(status_code=404, detail="Ticker not found")
    return {
        "symbol": info.get("symbol", "N/A"),
        "longName": info.get("longName", "N/A"),
        "currentPrice": info.get("currentPrice", "N/A"),
    }
