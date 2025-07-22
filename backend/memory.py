# backend/memory.py
from langchain_core.chat_history import InMemoryChatMessageHistory

memory_store = {}

def get_shared_memory(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in memory_store:
        memory_store[session_id] = InMemoryChatMessageHistory()
    return memory_store[session_id]
