from schemas import AgentState
from tools.rag_tools import ensure_vectorstore_built, retrieve_research_context

def rag_quant_node(state: AgentState) -> AgentState:
    state.setdefault("errors", [])
    ticker = state["ticker"]

    # Build or reuse vector store
    built = ensure_vectorstore_built()
    if not built["ok"]:
        state["errors"].append(f"RAG build error: {built['error']}")
        state["rag_context"] = None
        return state

    ctx = retrieve_research_context(query=f"{ticker} company outlook risks catalysts", k=6)
    if not ctx["ok"]:
        state["errors"].append(f"RAG retrieve error: {ctx['error']}")
        state["rag_context"] = None
        return state

    state["rag_context"] = ctx.get("data", "")
    return state