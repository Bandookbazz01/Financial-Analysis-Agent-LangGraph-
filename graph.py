from langgraph.graph import StateGraph, END
from schemas import AgentState

from agents.supervisor import supervisor_node
from agents.market_data import market_data_node
from agents.sentiment import sentiment_node
from agents.rag_quant import rag_quant_node
from agents.synthesizer import synthesizer_node

def route_to_agent(state: AgentState) -> str:
    # supervisor sets next_agent
    return state.get("next_agent", "synthesizer")

def build_app():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("market_data", market_data_node)
    graph.add_node("sentiment", sentiment_node)
    graph.add_node("rag_quant", rag_quant_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", route_to_agent)

    # loop-backs
    graph.add_edge("market_data", "supervisor")
    graph.add_edge("sentiment", "supervisor")
    graph.add_edge("rag_quant", "supervisor")

    graph.add_edge("synthesizer", END)

    return graph.compile()