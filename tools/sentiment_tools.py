from transformers import pipeline

_finbert = None

def _get_finbert():
    global _finbert
    if _finbert is None:
        _finbert = pipeline("text-classification", model="ProsusAI/finbert", truncation=True)
    return _finbert

def analyze_news_sentiment_finbert(news: list[dict]) -> dict:
    try:
        clf = _get_finbert()
        if not news:
            return {"ok": True, "data": {"overall": "unknown", "items": []}}

        items = []
        pos = neg = neu = 0

        for n in news:
            text = (n.get("title") or "") + "\n" + (n.get("content") or "")
            out = clf(text[:2000])[0]  # keep it safe
            label = out.get("label", "").lower()
            score = float(out.get("score", 0.0))

            if "positive" in label:
                pos += 1
            elif "negative" in label:
                neg += 1
            else:
                neu += 1

            items.append({
                "title": n.get("title"),
                "url": n.get("url"),
                "sentiment": label,
                "confidence": score,
            })

        overall = "neutral"
        if pos > max(neg, neu):
            overall = "positive"
        elif neg > max(pos, neu):
            overall = "negative"

        return {"ok": True, "data": {"overall": overall, "counts": {"pos": pos, "neg": neg, "neu": neu}, "items": items}}
    except Exception as e:
        return {"ok": False, "error": str(e), "data": {"overall": "unknown", "items": []}}