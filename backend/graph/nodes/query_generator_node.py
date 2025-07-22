# backend/graph/nodes/query_generator_node.py

from langchain_core.messages import AIMessage
from backend.graph.schema import AgentState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json # For formatting identified_columns/tables in prompt
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o", temperature=0)


query_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert SQL generator for a MySQL database.
Your task is to generate a SQL query based on the user's question,
incorporating identified tables, specific columns, and any extracted filters.

Focus solely on generating the raw SQL query, without any conversational text or markdown code block fences (```sql ```).

**Comprehensive Database Schema Information:**
- Table: `Supplier`
    - Columns: `supplier_id` (STRING, PK), `client_id` (INTEGER), `company_name` (STRING), `currency_code` (CHAR), `active_status` (INTEGER), `type` (INTEGER), `created_time` (DATETIME), `updated_time` (DATETIME), `tax_id` (STRING)
- Table: `Bill`
    - Columns: `bill_id` (STRING, PK), `client_id` (INTEGER), `supplier_id` (STRING, FK to Supplier.supplier_id), `txn_total_amount` (DECIMAL), `txn_date` (DATETIME), `currency_code` (CHAR), `exchange_rate` (DECIMAL), `home_total_amount` (DECIMAL), `payment_status` (INTEGER), `active_status` (INTEGER), `created_time` (DATETIME), `due_date` (DATETIME), `description` (STRING)
- Table: `Item`
    - Columns: `item_id` (STRING, PK), `client_id` (INTEGER), `item_name` (STRING), `full_name` (STRING), `item_type` (STRING), `purchase_cost` (DECIMAL), `unit_price` (DECIMAL), `active_status` (INTEGER)
- Table: `Bill_Line`
    - Columns: `line_id` (STRING, PK), `client_id` (INTEGER), `bill_id` (STRING, FK to Bill.bill_id), `item_id` (STRING, FK to Item.item_id), `account_id` (STRING), `description` (STRING), `amount` (DECIMAL), `quality` (DECIMAL), `unit_price` (DECIMAL), `billable` (BOOLEAN)
- Table: `Payment`
    - Columns: `payment_id` (STRING, PK), `client_id` (INTEGER), `txn_total_amount` (DECIMAL), `home_total_amount` (DECIMAL), `txn_date` (DATETIME), `currency_code` (CHAR), `exchange_rate` (DECIMAL), `active_status` (INTEGER), `void_status` (BOOLEAN)

**Relationships:**
- `Bill.supplier_id` references `Supplier.supplier_id`
- `Bill_Line.bill_id` references `Bill.bill_id`
- `Bill_Line.item_id` references `Item.item_id`

**Instructions for SQL Generation:**
- Use the `identified_tables` and `identified_columns` as strong hints for the primary focus of the query.
- Apply `fuzzy_filters` to the WHERE clause.
- Ensure proper JOINs when querying across related tables.
- Return only the SQL query string.
- When referring to supplier names, use `company_name`.
"""),
    ("human", """
    User Query: {question}
    Identified Tables: {identified_tables}
    Identified Columns: {identified_columns}
    Extracted Filters: {fuzzy_filters}
    """)
])


query_chain = query_prompt | llm

def query_generator_node(state: AgentState, config) -> dict:
    question = state.messages[-1].content
    
    # Provide default empty values if not set by previous nodes
    identified_tables = state.identified_tables or []
    identified_columns = state.identified_columns or {}
    fuzzy_filters = state.fuzzy_filters or {} # Assuming fuzzy_filter_node runs before this

    # Invoke the chain with all necessary context
    result = query_chain.invoke({
        "question": question,
        "identified_tables": json.dumps(identified_tables), 
        "identified_columns": json.dumps(identified_columns),
        "fuzzy_filters": json.dumps(fuzzy_filters)
    }, config=config)

    sql_output = result.content
    state.messages.append(AIMessage(content=f"Generated SQL: ```sql\n{sql_output}\n```"))

    state.sql_query_to_execute = sql_output

    next_node = "sql_executor"

    return {
        "messages": state.messages,
        "visited_nodes": state.visited_nodes,
        "next": next_node,
        "sql_query_to_execute": state.sql_query_to_execute
    }