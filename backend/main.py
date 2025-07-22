from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from backend.graph.builder import build_graph
from backend.graph.schema import AgentState
from backend.memory import get_shared_memory  # Make sure this is actually imported
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class Query(BaseModel):
    question: str

graph = build_graph()

# ✅ Normalize messages before using in AgentState
def normalize_messages(messages):
    normalized = []
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                normalized.append(HumanMessage(content=content))
            elif role == "system":
                normalized.append(AIMessage(content=content))
            else:
                normalized.append(AIMessage(content=content))
        else:
            normalized.append(msg)
    return normalized

@app.post("/ask")
async def ask_agent(query: Query):
    session_id = "user-1"
    chat_history = get_shared_memory(session_id).messages

    # Add new user message
    chat_history.append(HumanMessage(content=query.question))

    # ✅ Normalize chat history before passing to graph
    normalized_messages = normalize_messages(chat_history)

    state_input = AgentState(
        messages=normalized_messages,
        visited_nodes=[],
        next_nodes=[]
    )

    response = graph.invoke(
        state_input,
        config={"configurable": {"session_id": session_id}},
    )

    messages = response.get("messages", [])
    last_message = messages[-1] if messages else None

    return {
        "input": query.question,
        "output": last_message.content if hasattr(last_message, "content") else str(last_message)
    }
