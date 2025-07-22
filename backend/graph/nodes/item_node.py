# backend/graph/nodes/item_node.py

from backend.graph.schema import AgentState
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o", temperature=0)
parser = JsonOutputParser()


item_schema_extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an expert in understanding user queries related to the `Item` table.
    Your task is to identify the relevant tables and columns based on the user's question.

    **Database Schema Information:**
    - Table: `Item`
        - Columns: `item_id` (STRING, PK), `client_id` (INTEGER), `item_name` (STRING),
                   `full_name` (STRING), `item_type` (STRING), `purchase_cost` (DECIMAL),
                   `unit_price` (DECIMAL), `active_status` (INTEGER)
    - Table: `Bill_Line` (for potential joins, if relevant to items in a bill context)
        - Columns: `line_id` (STRING, PK), `client_id` (INTEGER), `bill_id` (STRING, FK),
                   `item_id` (STRING, FK to Item.item_id), `amount` (DECIMAL), `quality` (DECIMAL)

    Output your findings as a JSON object with the following structure:
    {{
        "relevant_tables": ["Item"], // Always include "Item" if relevant, potentially "Bill_Line"
        "identified_columns": {{ // Map table names to a list of relevant columns
            "Item": ["list_of_relevant_columns_from_item_table"],
            "Bill_Line": ["list_of_relevant_columns_from_bill_line_table"] // Only if relevant for joins
        }}
    }}
    If no specific columns are mentioned but the query clearly relates to items,
    return a default set of common columns like `item_id`, `item_name`, `unit_price`.
    """),
    ("human", "{question}")
])

item_schema_extractor_chain = item_schema_extraction_prompt | llm | parser

def get_latest_user_input(messages):
    """Helper to extract user input from message list (supports dict or LangChain message)."""
    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        return last_msg.get("content", "")
    elif hasattr(last_msg, "content"):
        return last_msg.content
    else:
        return str(last_msg)

def item_node(state: AgentState, config) -> dict:
    query = get_latest_user_input(state.messages)

    try:
        extracted_schema_info = item_schema_extractor_chain.invoke({"question": query})
        
        identified_tables = extracted_schema_info.get("relevant_tables", [])
        identified_columns = extracted_schema_info.get("identified_columns", {})

        
        if "Item" not in identified_tables:
            identified_tables.append("Item")
        if "Item" not in identified_columns or not isinstance(identified_columns["Item"], list):
            identified_columns["Item"] = ["item_id", "item_name", "unit_price"]

        print(f"DEBUG: Item Node identified tables: {identified_tables}")
        print(f"DEBUG: Item Node identified columns: {identified_columns}")

    except Exception as e:
        print(f"ERROR: Item Node schema extraction failed: {e}")
        identified_tables = ["Item"]
        identified_columns = {"Item": ["item_id", "item_name", "unit_price"]}

    return {
        "messages": state.messages,
        "visited_nodes": state.visited_nodes + ["item"], 
        "identified_tables": identified_tables,
        "identified_columns": identified_columns,
        "next": "filter_check"
    }