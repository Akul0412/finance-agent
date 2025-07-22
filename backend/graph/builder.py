from langgraph.graph import StateGraph, END
from backend.graph.schema import AgentState

# Node imports
from backend.graph.nodes.supplier_node import supplier_node
from backend.graph.nodes.bill_node import bill_node
from backend.graph.nodes.item_node import item_node
from backend.graph.nodes.knowledge_node import knowledge_node
from backend.graph.nodes.router_node import router_node
from backend.graph.nodes.filter_check_node import filter_check_node
from backend.graph.nodes.fuzzy_filter_node import fuzzy_filter_node
from backend.graph.nodes.query_generator_node import query_generator_node
from backend.graph.nodes.sql_executor_node import sql_executor_node # New import!

# backend/graph/builder.py
def route_next(state: AgentState) -> str:
    return state.next

def route_after_filter(state: AgentState) -> str:
    return state.next

def build_graph():
    graph = StateGraph(AgentState)

    graph.set_entry_point("router")

    graph.add_node("router", router_node)
    graph.add_node("supplier", supplier_node)
    graph.add_node("bill", bill_node)
    graph.add_node("item", item_node)
    graph.add_node("knowledge", knowledge_node)
    graph.add_node("filter_check", filter_check_node)
    graph.add_node("fuzzy_filter", fuzzy_filter_node)
    graph.add_node("query_generator", query_generator_node)
    graph.add_node("sql_executor", sql_executor_node) # New node added!

   
    graph.add_conditional_edges("router", route_next, {
        "supplier": "supplier",
        "bill": "bill",
        "item": "item",
        "knowledge": "knowledge",
        END: END
    })

   
    for node in ["supplier", "bill", "item", "knowledge"]:
        graph.add_edge(node, "filter_check")

    
    graph.add_conditional_edges("filter_check", route_after_filter, {
        "fuzzy_filter": "fuzzy_filter",
        "query_generator": "query_generator",
        END: END
    })

    graph.add_edge("fuzzy_filter", "query_generator")

    
    graph.add_edge("query_generator", "sql_executor") 

    
    graph.add_edge("sql_executor", END) 

    return graph.compile()