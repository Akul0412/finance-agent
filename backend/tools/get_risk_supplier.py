from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))

risk_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert assistant that identifies high-risk suppliers based on client-specific criteria.

You have access to metadata about:
- single source suppliers
- suppliers with high total spend
- frequently used suppliers (operational reliance)
- long-term relationships (>3 years)

Your job is to interpret the user's request and summarize which suppliers may be high-risk.

NEVER fabricate supplier names or IDs — only describe the reasoning process or return fallback if not available.

If the question mentions filters like 'single source', 'long-term', 'total spend', or 'frequent usage', use that to infer risk factors.

If you need to ask for client_id or more filters, do so.
    """),
    ("human", "{input}")
])

risk_chain = risk_prompt | llm | StrOutputParser()

@tool
def get_risk_supplier(input: str) -> str:
    """Analyze high-risk supplier conditions based on user input."""
    return risk_chain.invoke({"input": input})

# EXPORT TOOL
get_risk_supplier_tool = get_risk_supplier
