# backend/graph/nodes/bill_node.py

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

# Prompt for the internal LLM of bill_node to identify tables/columns
bill_schema_extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an expert in understanding user queries related to the `Bill` and `Bill_Line` tables.
    Your task is to identify the relevant tables and columns based on the user's question.

    **Database Schema Information:**
    - Table: `Bill`
        - Columns: `bill_id` (STRING, PK), `client_id` (INTEGER), `supplier_id` (STRING, FK to Supplier.supplier_id),
                   `txn_total_amount` (DECIMAL), `txn_date` (DATETIME), `currency_code` (CHAR),
                   `exchange_rate` (DECIMAL), `home_total_amount` (DECIMAL), `payment_status` (INTEGER),
                   `active_status` (INTEGER), `created_time` (DATETIME), `due_date` (DATETIME),
                   `description` (STRING)
    - Table: `Bill_Line`
        - Columns: `line_id` (STRING, PK), `client_id` (INTEGER), `bill_id` (STRING, FK to Bill.bill_id),
                   `item_id` (STRING, FK to Item.item_id), `account_id` (STRING), `description` (STRING),
                   `amount` (DECIMAL), `quality` (DECIMAL), `unit_price` (DECIMAL), `billable` (BOOLEAN)

    Output your findings as a JSON object with the following structure:
    {{
        "relevant_tables": ["Bill"], // Always include "Bill" if relevant, potentially "Bill_Line", "Supplier", "Item" for joins
        "identified_columns": {{ // Map table names to a list of relevant columns
            "Bill": ["list_of_relevant_columns_from_bill_table"],
            "Bill_Line": ["list_of_relevant_columns_from_bill_line_table"] // Only if relevant
        }}
    }}
    If no specific columns are mentioned but the query clearly relates to bills,
    return a default set of common columns like `bill_id`, `txn_total_amount`, `txn_date`.
    """),
    ("human", "{question}")
])

bill_schema_extractor_chain = bill_schema_extraction_prompt | llm | parser

def get_latest_user_input(messages):
    """Helper to extract user input from message list (supports dict or LangChain message)."""
    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        return last_msg.get("content", "")
    elif hasattr(last_msg, "content"):
        return last_msg.content
    else:
        return str(last_msg)

def bill_node(state: AgentState, config) -> dict:
    query = get_latest_user_input(state.messages)

    try:
        extracted_schema_info = bill_schema_extractor_chain.invoke({"question": query})
        
        identified_tables = extracted_schema_info.get("relevant_tables", [])
        identified_columns = extracted_schema_info.get("identified_columns", {})

        
        if "Bill" not in identified_tables:
            identified_tables.append("Bill")
        if "Bill" not in identified_columns or not isinstance(identified_columns["Bill"], list):
            identified_columns["Bill"] = ["bill_id", "txn_total_amount", "txn_date"]

        print(f"DEBUG: Bill Node identified tables: {identified_tables}")
        print(f"DEBUG: Bill Node identified columns: {identified_columns}")

    except Exception as e:
        print(f"ERROR: Bill Node schema extraction failed: {e}")
        identified_tables = ["Bill"]
        identified_columns = {"Bill": ["bill_id", "txn_total_amount", "txn_date"]}

    return {
        "messages": state.messages,
        "visited_nodes": state.visited_nodes + ["bill"], 
        "identified_tables": identified_tables,
        "identified_columns": identified_columns,
        "next": "filter_check" 
    }