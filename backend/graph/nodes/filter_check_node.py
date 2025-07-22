# backend/graph/nodes/filter_check_node.py

from backend.graph.schema import AgentState
from langgraph.graph import END 

def get_latest_user_input(messages):
    """Safely extract user input from last message (LangChain or dict)."""
    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        return last_msg.get("content", "")
    elif hasattr(last_msg, "content"):
        return last_msg.content
    else:
        return str(last_msg)

def filter_check_node(state: AgentState, config) -> dict:
    user_input = get_latest_user_input(state.messages)

    
    needs_filter = "where" in user_input.lower() or "filter" in user_input.lower() or "filters" in user_input.lower()

    next_step = None
    if needs_filter:
        next_step = "fuzzy_filter"
    else:
        
        next_step = "query_generator"

    return {
        "messages": state.messages,
        "visited_nodes": state.visited_nodes,
        "filter_passed": needs_filter, 
        "next": next_step 
    }