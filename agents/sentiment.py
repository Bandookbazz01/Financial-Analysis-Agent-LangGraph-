from schemas import AgentState
from tools.news_tools import fetch_company_news
from tools.sentiment_tools import analyze_news_sentiment_finbert

def sentiment_node(state: AgentState) -> AgentState:
    ticker = state["ticker"]
    state.setdefault("errors", [])

    news_res = fetch_company_news(ticker, max_results=6)
    if not news_res["ok"]:
        state["errors"].append(f"News fetch error: {news_res['error']}")
    news = news_res.get("data", []) or []
    state["news"] = news

    sent_res = analyze_news_sentiment_finbert(news)
    if not sent_res["ok"]:
        state["errors"].append(f"Sentiment error: {sent_res['error']}")
    state["sentiment"] = sent_res.get("data", {}) or {}

    return state