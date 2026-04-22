from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict, total=False):
    ticker: str

    # data gathered
    market: Dict[str, Any]
    indicators: Dict[str, Any]
    news: List[Dict[str, Any]]
    sentiment: Dict[str, Any]
    rag_enabled: bool
    rag_context: Optional[str]

    # orchestration
    next_agent: Optional[str]
    iterations: int
    max_iterations: int

    # output + errors
    report: Optional[str]
    errors: List[str]
    last_updated_utc: str