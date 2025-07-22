from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import SessionLocal  
from backend.models import Supplier, Bill
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool


class GetSpendInput(BaseModel):
    client_id: int = Field(..., description="The client ID to check which suppliers they have access to")
    top_n: int = Field(description="Top N suppliers by total spend")

def get_high_spend_suppliers(client_id: int, top_n: int) -> str:
    db: Session = SessionLocal()
    try:
        results = (
            db.query(
                Supplier.company_name,
                func.sum(Bill.home_total_amount).label("total_spend")
            )
            .join(Bill, Supplier.supplier_id == Bill.supplier_id)
            .filter(Bill.client_id == client_id)
            .group_by(Supplier.company_name)
            .order_by(func.sum(Bill.home_total_amount).desc())
            .limit(top_n)
            .all()
        )

        if not results:
            return f"No spending data found for client ID {client_id}."

        output = f"Top {top_n} high-spend suppliers for client ID {client_id}:\n"
        for company_name, total_spend in results:
            output += f"- {company_name}: ${float(total_spend):,.2f}\n"

        return output.strip()
    
    finally:
        db.close()


get_high_spend_suppliers_tool = StructuredTool.from_function(
    func=get_high_spend_suppliers,
    name="get_high_spend_suppliers",
    description="Returns the top N high-spend suppliers for a given client_id.",
    args_schema=GetSpendInput
)
