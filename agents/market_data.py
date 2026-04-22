from schemas import AgentState
from tools.stock_tools import fetch_market_data
from tools.indicator_tools import compute_indicators

def market_data_node(state: AgentState) -> AgentState:
    ticker = state["ticker"]
    state.setdefault("errors", [])

    m = fetch_market_data(ticker)
    if not m["ok"]:
        state["errors"].append(f"Market data error: {m['error']}")
    state["market"] = m.get("data", {}) or {}

    ind = compute_indicators(ticker)
    if not ind["ok"]:
        state["errors"].append(f"Indicator error: {ind['error']}")
    state["indicators"] = ind.get("data", {}) or {}

    return state