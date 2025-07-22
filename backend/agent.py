# backend/agent.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=api_key)

def make_executor(system_msg: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "{input}")
    ])
    return prompt | llm | StrOutputParser()


supplier_executor = make_executor(
    "You are an expert in the Supplier table. Answer questions about supplier company names, status, tax IDs, and creation dates."
)

bill_executor = make_executor(
    "You are an expert in the Bill table. Answer questions about bill totals, due dates, supplier linkage, and bill descriptions."
)

item_executor = make_executor(
    "You are an expert in the Item table. Answer questions about item names, pricing, types, and purchase costs."
)

bill_line_executor = make_executor(
    "You are an expert in the Bill_Line table. Answer questions about individual bill items, their quantities, prices, and item linkage."
)

payment_executor = make_executor(
    "You are an expert in the Payment table. Answer questions about transaction amounts, payment dates, and void status."
)



