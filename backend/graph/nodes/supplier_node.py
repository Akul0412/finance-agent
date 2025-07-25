# backend/graph/nodes/supplier_node.py

from backend.graph.schema import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser # New import for parsing structured output
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0)


parser = JsonOutputParser()


supplier_schema_extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an expert in understanding user queries related to the `Supplier` table.
    Your task is to identify the relevant tables and columns based on the user's question.

    **Database Schema Information:**
    - Table: `Supplier`
        - Columns: `supplier_id` (STRING), `client_id` (INTEGER), `company_name` (STRING),
                   `currency_code` (CHAR), `active_status` (INTEGER), `type` (INTEGER),
                   `created_time` (DATETIME), `updated_time` (DATETIME), `tax_id` (STRING)

    Output your findings as a JSON object with the following structure:
    {{
        "relevant_tables": ["Supplier"], // Always include "Supplier" if relevant
        "identified_columns": {{ // Map table names to a list of relevant columns
            "Supplier": ["list_of_relevant_columns_from_supplier_table"]
        }}
    }}
    If no specific columns are mentioned but the query clearly relates to suppliers,
    return a default set of common columns like `supplier_id`, `company_name`, `active_status`.
    """),
    ("human", "{question}")
])

supplier_schema_extractor_chain = supplier_schema_extraction_prompt | llm | parser

def get_latest_user_input(messages):
    """Handles both LangChain Message objects and plain dicts."""
    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        return last_msg.get("content", "")
    elif hasattr(last_msg, "content"):
        return last_msg.content
    else:
        return str(last_msg)

def supplier_node(state: AgentState, config) -> dict:
    user_input = get_latest_user_input(state.messages)

    try:
        extracted_schema_info = supplier_schema_extractor_chain.invoke({"question": user_input})
    
        print("Trying Suppliers Node")
        
        identified_tables = extracted_schema_info.get("relevant_tables", [])
        identified_columns = extracted_schema_info.get("identified_columns", {})

        
        if "Supplier" not in identified_tables:
            identified_tables.append("Supplier")
        
       
        if "Supplier" not in identified_columns or not isinstance(identified_columns["Supplier"], list):
            
            identified_columns["Supplier"] = ["supplier_id", "company_name", "active_status"]

        print(f"DEBUG: Supplier Node identified tables: {identified_tables}")
        print(f"DEBUG: Supplier Node identified columns: {identified_columns}")

    except Exception as e:
        print(f"ERROR: Supplier Node schema extraction failed: {e}")
       
        identified_tables = ["Supplier"]
        identified_columns = {"Supplier": ["supplier_id", "company_name", "active_status"]}
        

    
    return {
        "messages": state.messages, 
        "visited_nodes": state.visited_nodes,
        "identified_tables": identified_tables,
        "identified_columns": identified_columns,
        "next": "filter_check"
    }