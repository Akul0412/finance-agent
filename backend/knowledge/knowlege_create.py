import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Load environment variables (for OpenAI API key)
load_dotenv()

# Path to your markdown knowledge file
kb_path = "backend/knowledge/knowledge_base.md"
index_path = "backend/knowledge/knowledge_index"

# Read markdown content
with open(kb_path, "r", encoding="utf-8") as f:
    kb_text = f.read()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split_text(kb_text)
docs = [Document(page_content=chunk) for chunk in chunks]

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(docs, embeddings)

# Save FAISS index
vectorstore.save_local(index_path)

print(f"✅ Knowledge base indexed and saved to: {index_path}")
