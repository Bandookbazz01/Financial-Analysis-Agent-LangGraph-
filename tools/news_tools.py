import finnhub
from config import FINNHUB_API_KEY
from datetime import datetime, timedelta

def fetch_company_news(ticker: str, max_results: int = 6) -> dict:
    try:
        if not FINNHUB_API_KEY:
            return {"ok": False, "error": "Missing FINNHUB_API_KEY", "data": []}

        client = finnhub.Client(api_key=FINNHUB_API_KEY)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # finnhub format: YYYY-MM-DD
        _from = start_date.strftime('%Y-%m-%d')
        _to = end_date.strftime('%Y-%m-%d')
        
        res = client.company_news(ticker, _from=_from, to=_to)
        
        items = []
        for i, r in enumerate(res):
            if i >= max_results:
                break
            items.append({
                "title": r.get("headline"),
                "url": r.get("url"),
                "content": r.get("summary"),
                "score": 1.0, # no confidence score provided by finnhub
            })
        return {"ok": True, "data": items}
    except Exception as e:
        return {"ok": False, "error": str(e), "data": []}