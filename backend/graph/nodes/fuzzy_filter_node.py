from backend.graph.schema import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=api_key)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an assistant that extracts WHERE-clause-style filters from a natural language query for use in SQL.

Only return a dictionary of filter keys and values. Example:
{"supplier_name": "ACME Corp", "date_range": "2023-01 to 2023-12"}

If no filters are present, return an empty dictionary: {}
"""),
    ("human", "{question}")
])

chain = prompt | llm | StrOutputParser()

def get_latest_user_input(messages):
    """Extracts user input regardless of message type."""
    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        return last_msg.get("content", "")
    elif hasattr(last_msg, "content"):
        return last_msg.content
    else:
        return str(last_msg)

def fuzzy_filter_node(state: AgentState, config) -> dict:
    question = get_latest_user_input(state.messages)
    print(f"DEBUG: Entering fuzzy_filter_node with query: {question}")
    extracted_filters = chain.invoke({"question": question})

    return {
        "messages": state.messages,
        "fuzzy_filters": eval(extracted_filters),
        "visited_nodes": state.visited_nodes
    }
