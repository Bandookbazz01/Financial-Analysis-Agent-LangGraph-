from schemas import AgentState
from prompts import SYNTHESIS_PROMPT
from langchain_core.prompts import PromptTemplate
from config import GROQ_API_KEY, GROQ_MODEL, GOOGLE_API_KEY
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

def compute_recommendation(ind: dict, sent: dict, market: dict) -> tuple[str, str]:
    score = 0
    reasons = []

    # RSI Logic
    rsi = ind.get("rsi_14_latest")
    if rsi is not None:
        if rsi < 30:
            score += 1
            reasons.append("RSI indicates oversold conditions (+1).")
        elif rsi > 70:
            score -= 1
            reasons.append("RSI indicates overbought conditions (-1).")
        else:
            reasons.append("RSI is neutral (0).")
            
    # MACD Logic
    macd = ind.get("macd_latest")
    signal = ind.get("macd_signal_latest")
    if macd is not None and signal is not None:
        if macd > signal:
            score += 1
            reasons.append("MACD is above signal line (bullish crossover) (+1).")
        else:
            score -= 1
            reasons.append("MACD is below signal line (bearish crossover) (-1).")

    # Sentiment Logic
    overall_sentiment = sent.get("overall", "neutral")
    if overall_sentiment == "positive":
        score += 1
        reasons.append("Overall news sentiment is positive (+1).")
    elif overall_sentiment == "negative":
        score -= 1
        reasons.append("Overall news sentiment is negative (-1).")
    else:
        reasons.append("Overall news sentiment is neutral (0).")

    # P/E Logic
    trailing_pe = market.get("trailingPE")
    if trailing_pe:
        if 0 < trailing_pe < 15:
            score += 1
            reasons.append("P/E ratio is favorable (< 15) (+1).")
        elif trailing_pe > 30:
            score -= 1
            reasons.append("P/E ratio is high (> 30) (-1).")
            
    if score >= 2:
        rec = "BUY"
    elif score <= -2:
        rec = "SELL"
    else:
        rec = "HOLD"
        
    reasoning = "\n".join(reasons) + f"\nTotal Score: {score}"
    return rec, reasoning

def synthesizer_node(state: AgentState) -> AgentState:
    state.setdefault("errors", [])

    ticker = state.get("ticker", "")
    market = state.get("market", {}) or {}
    ind = state.get("indicators", {}) or {}
    news = state.get("news", []) or []
    sent = state.get("sentiment", {}) or {}
    rag = state.get("rag_context") or ""
    ts = state.get("last_updated_utc", "")

    rec, reasoning = compute_recommendation(ind, sent, market)
    rule_based_recommendation = f"Recommendation: {rec}\nReasoning:\n{reasoning}"

    # Prepare context for LLM
    prompt_val = PromptTemplate.from_template(SYNTHESIS_PROMPT).format(
        ticker=ticker,
        market=str(market),
        indicators=str(ind),
        news=str(news[:5]),  # Limit to avoid huge context
        sentiment=str(sent),
        rag_context=str(rag),
        errors=str(state.get("errors", [])),
        last_updated_utc=str(ts),
        rule_based_recommendation=rule_based_recommendation
    )

    llm_report = None
    try:
        # Primary: Groq
        if GROQ_API_KEY:
            llm = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY)
            
            # Fallback to Gemini if configured
            if GOOGLE_API_KEY:
                fallback_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)
                llm = llm.with_fallbacks([fallback_llm])
            
            res = llm.invoke(prompt_val)
            llm_report = res.content
    except Exception as e:
        state["errors"].append(f"LLM Generation Error: {str(e)}")

    if not llm_report:
        # Fallback text if LLM completely fails
        llm_report = f"LLM Generation Failed. Here is the rule-based recommendation:\n{rule_based_recommendation}"

    state["report"] = llm_report
    return state