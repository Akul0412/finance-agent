from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import SessionLocal
from backend.models import Supplier, Bill
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool


class FrequentSuppliersInput(BaseModel):
    client_id: int = Field(..., description="The client ID to check supplier usage for")
    top_n: int = Field(5, description="Top N most frequently used suppliers")


def get_frequent_suppliers(client_id: int, top_n: int) -> str:
    db: Session = SessionLocal()
    try:
        results = (
            db.query(
                Supplier.company_name,
                func.count(Bill.bill_id).label("bill_count")
            )
            .join(Bill, Supplier.supplier_id == Bill.supplier_id)
            .filter(Bill.client_id == client_id)
            .group_by(Supplier.company_name)
            .order_by(func.count(Bill.bill_id).desc())
            .limit(top_n)
            .all()
        )

        if not results:
            return f"No suppliers found with billing activity for client ID {client_id}."

        output = f"Top {top_n} most frequently used suppliers for client ID {client_id}:\n"
        for company_name, bill_count in results:
            output += f"- {company_name}: {bill_count} bills\n"

        return output.strip()
    
    finally:
        db.close()
get_frequent_suppliers_tool = StructuredTool.from_function(
    func=get_frequent_suppliers,
    name="get_frequent_suppliers",
    description="Returns the top N suppliers that appear most frequently in bills for a given client_id.",
    args_schema=FrequentSuppliersInput
)
