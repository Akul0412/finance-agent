# backend/graph/nodes/router_node.py

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableMap
from langchain_core.messages import AIMessage
from backend.graph.schema import AgentState
from langgraph.graph import END
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

template = ChatPromptTemplate.from_messages([
    ("system", """
You are an intelligent router for a supplier analytics assistant.

Output ONLY a Python list of strings representing the nodes to route through.
Example: ['supplier', 'bill', 'query_generator']
Never include any explanation, markdown, or quotes.
"""),
    ("human", "{question}")
])

router_chain = (
    RunnableMap({"question": lambda x: x["question"]})
    | template
    | llm
    | StrOutputParser()
)

def router_node(state: AgentState, config) -> AgentState:
    question = state.messages[-1].content

    if not state.visited_nodes:
        raw = router_chain.invoke({"question": question})
        cleaned = raw.replace("```python", "").replace("```", "").strip()
        try:
            routes = eval(cleaned)
        except Exception:
            routes = []

        state.visited_nodes = routes

    next_node = state.visited_nodes.pop(0) if state.visited_nodes else END

    return AgentState(
        messages=state.messages,
        visited_nodes=state.visited_nodes,
        next=next_node
    )
