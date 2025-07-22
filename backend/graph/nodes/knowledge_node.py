from langchain_core.messages import AIMessage
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from backend.graph.schema import AgentState
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load the FAISS vectorstore from the saved directory
vectorstore = FAISS.load_local(
    "backend/knowledge/knowledge_index",
    embeddings=OpenAIEmbeddings(),
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Prompt template for QA over context
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer using only the following knowledge snippets:\n{context}"),
    ("human", "{input}")
])

qa_chain = (
    {"input": lambda x: x["question"], "context": lambda x: "\n\n".join(x["docs"])}
    | prompt
    | llm
    | StrOutputParser()
)

def get_latest_user_input(messages):
    """Helper to extract user input from message list (handles dict or LC Message)."""
    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        return last_msg.get("content", "")
    elif hasattr(last_msg, "content"):
        return last_msg.content
    else:
        return str(last_msg)

def knowledge_node(state: AgentState, config) -> AgentState:
    query = get_latest_user_input(state.messages)
    docs = retriever.invoke(query)
    doc_contents = [doc.page_content for doc in docs]

    answer = qa_chain.invoke({"question": query, "docs": doc_contents})

    return AgentState(
        messages=state.messages + [AIMessage(content=answer)],
        visited_nodes=state.visited_nodes + ["knowledge"]
    )
