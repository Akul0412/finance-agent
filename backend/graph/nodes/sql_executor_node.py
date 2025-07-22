import os

import re
from backend.graph.schema import AgentState
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END


from backend.database import SessionLocal 
from sqlalchemy import text 

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
def extract_sql_query(text_with_sql: str) -> str:
    """
    Extracts the SQL query from a string that may contain conversational text
    and markdown code blocks (```sql ... ```).
    """
   
    match = re.search(r"```sql\s*(.*?)\s*```", text_with_sql, re.DOTALL)
    if match:
        return match.group(1).strip()
    
   
    return text_with_sql.strip()


def sql_executor_node(state: AgentState) -> dict:
    raw_llm_output = state.sql_query_to_execute
    messages = list(state.messages) 

    if not raw_llm_output:
        messages.append(AIMessage(content="Error: No SQL query to execute provided by the agent."))
        return {"messages": messages, "next": END}

   
    sql_query = extract_sql_query(raw_llm_output)
    if not sql_query:
        messages.append(AIMessage(content="Error: Failed to extract a valid SQL query from the agent's output."))
        return {"messages": messages, "next": END}
 

    db = None
    results = None
    error_message = None

    try:
        db = SessionLocal() 
        print(f"DEBUG: Attempting to execute clean SQL: {sql_query}") 

        
        result_proxy = db.execute(text(sql_query))

        
        if sql_query.strip().upper().startswith("SELECT"):
            rows = result_proxy.fetchall()
            
            if rows:
                # Get column names dynamically
                columns = result_proxy.keys()
                
                formatted_results = []
                formatted_results.append("| " + " | ".join(columns) + " |")
                formatted_results.append("|" + "---|"*len(columns))
                for row in rows:
                    # Convert row to dictionary for easier access/storage
                    row_dict = dict(zip(columns, row))
                    formatted_results.append("| " + " | ".join(str(row_dict[col]) for col in columns) + " |")
                
                response_content = "Query executed successfully. Here are the results:\n" + "\n".join(formatted_results)
                results = [dict(zip(columns, row)) for row in rows] # Store as list of dicts
            else:
                response_content = "Query executed successfully, but returned no results."
                results = []
        else:
           
            db.commit()
            response_content = f"Query executed successfully. Rows affected: {result_proxy.rowcount}"
            results = f"Rows affected: {result_proxy.rowcount}"

        messages.append(AIMessage(content=response_content))
        state.query_result = results

    except Exception as e:
        if db: 
            db.rollback() 
        error_message = f"SQL execution error with SQLAlchemy: {str(e)}"
        messages.append(AIMessage(content=error_message))
        state.query_result = {"error": error_message}
    finally:
        if db:
            db.close() 

    return {
        "messages": messages,
        "next": END,
        "query_result": state.query_result
    }

