# backend/graph/schema.py

from typing import List, Optional, Any, Dict
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

class AgentState(BaseModel):
    messages: List[BaseMessage]
    visited_nodes: List[str] = []
    next: Optional[str] = None
    sql_query_to_execute: Optional[str] = None
    query_result: Optional[Any] = None
    identified_tables: Optional[List[str]] = None
    identified_columns: Optional[Dict[str, List[str]]] = None
    fuzzy_filters: Optional[Dict[str, Any]] = None # This will store the extracted filters (e.g., {"company_name": "ACME Corp"})
    