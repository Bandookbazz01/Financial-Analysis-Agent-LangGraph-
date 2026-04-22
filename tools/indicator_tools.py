import pandas as pd
import yfinance as yf
import pandas_ta as ta

def compute_indicators(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="6mo", interval="1d")
        if hist is None or hist.empty:
            return {"ok": False, "error": "No OHLCV data returned from yfinance.", "data": {}}

        close = hist["Close"]
        high = hist["High"]
        low = hist["Low"]
        volume = hist["Volume"]

        rsi = ta.rsi(close, length=14)
        macd = ta.macd(close)
        vwap = ta.vwap(high=high, low=low, close=close, volume=volume)

        data = {
            "rsi_14_latest": float(rsi.dropna().iloc[-1]) if rsi is not None and not rsi.dropna().empty else None,
            "macd_latest": float(macd["MACD_12_26_9"].dropna().iloc[-1]) if macd is not None else None,
            "macd_signal_latest": float(macd["MACDs_12_26_9"].dropna().iloc[-1]) if macd is not None else None,
            "macd_hist_latest": float(macd["MACDh_12_26_9"].dropna().iloc[-1]) if macd is not None else None,
            "vwap_latest": float(vwap.dropna().iloc[-1]) if vwap is not None and not vwap.dropna().empty else None,
        }
        return {"ok": True, "data": data}
    except Exception as e:
        return {"ok": False, "error": str(e), "data": {}}