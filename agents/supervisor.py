from datetime import datetime, timezone
from schemas import AgentState

def supervisor_node(state: AgentState) -> AgentState:
    iterations = state.get("iterations", 0) + 1
    max_iterations = state.get("max_iterations", 8)

    state["iterations"] = iterations
    state["last_updated_utc"] = datetime.now(timezone.utc).isoformat()

    if iterations >= max_iterations:
        state["next_agent"] = "synthesizer"
        state.setdefault("errors", []).append("Max iterations reached; synthesizing with partial data.")
        return state

    # Routing rules (deterministic)
    if not state.get("market") or not state.get("indicators"):
        state["next_agent"] = "market_data"
        return state

    if not state.get("news") or not state.get("sentiment"):
        state["next_agent"] = "sentiment"
        return state

    if state.get("rag_enabled", False) and not state.get("rag_context"):
        state["next_agent"] = "rag_quant"
        return state

    state["next_agent"] = "synthesizer"
    return state