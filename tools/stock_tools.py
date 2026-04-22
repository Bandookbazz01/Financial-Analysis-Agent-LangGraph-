import yfinance as yf
import finnhub
from config import FINNHUB_API_KEY

def fetch_market_data(ticker: str) -> dict:
    try:
        # yfinance history/technicals
        t = yf.Ticker(ticker)
        info = t.info or {}

        data = {
            "currentPrice": info.get("currentPrice"),
            "previousClose": info.get("previousClose"),
            "marketCap": info.get("marketCap"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "beta": info.get("beta"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "currency": info.get("currency"),
            "longName": info.get("longName"),
        }
        
        # Finnhub real-time quote + fundamentals override
        if FINNHUB_API_KEY:
            try:
                finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
                quote = finnhub_client.quote(ticker)
                if quote and 'c' in quote and quote['c']:
                    data["currentPrice"] = quote['c']
                    data["previousClose"] = quote['pc']
                    
                profile = finnhub_client.company_profile2(symbol=ticker)
                if profile:
                    data["marketCap"] = profile.get('marketCapitalization', data.get("marketCap"))
                    data["longName"] = profile.get('name', data.get("longName"))
                    data["industry"] = profile.get('finnhubIndustry', data.get("industry"))
            except Exception as e:
                print(f"Finnhub fetch error: {e}")

        return {"ok": True, "data": data}
    except Exception as e:
        return {"ok": False, "error": str(e), "data": {}}