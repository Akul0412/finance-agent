from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from langchain_core.messages import HumanMessage, AIMessage
from backend.graph.builder import build_graph
from backend.graph.schema import AgentState
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class Query(BaseModel):
    question: str
    history: List[Dict[str, str]]  # List of {'role': 'user' | 'assistant', 'content': str}

graph = build_graph()

def normalize_messages(messages: List[Dict[str, str]]):
    normalized = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            normalized.append(HumanMessage(content=content))
        elif role == "assistant":
            normalized.append(AIMessage(content=content))
    return normalized

@app.post("/ask")
async def ask_agent(query: Query):
    start = time.time()

    # Convert history to proper message objects and append current user message
    messages = normalize_messages(query.history)
    print(HumanMessage(content=query.question))
    messages.append(HumanMessage(content=query.question))


    state_input = AgentState(
        messages=messages,
        visited_nodes=[],
        next_nodes=[]
    )

    response = graph.invoke(state_input)

    last_msg = response.get("messages", [])[-1] if response.get("messages") else None

    end = time.time()
    print(f"[Timing] Prompt took {end - start:.2f} seconds")

    return {
        "input": query.question,
        "output": last_msg.content if hasattr(last_msg, "content") else str(last_msg),
    }
