from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class SpendAnalyticsInput(BaseModel):
    client_id: int = Field(..., description="The client ID for authentication and access control")
    supplier_name: str = Field(..., description="Name of the supplier")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")

def get_total_spend_by_supplier(client_id: int, supplier_name: str, start_date: str, end_date: str) -> str:
    from datetime import datetime
    from backend.database import SessionLocal
    from backend.models import Supplier, Bill

    try:
        start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return "Dates must be in YYYY-MM-DD format."

    db = SessionLocal()
    try:
        # Resolve supplier_id using client_id + supplier_name
        supplier = (
            db.query(Supplier)
            .filter(Supplier.client_id == client_id)
            .filter(Supplier.company_name.ilike(f"%{supplier_name}%"))
            .first()
        )

        if not supplier:
            return f"Supplier '{supplier_name}' not found for client ID {client_id}."

        total = (
            db.query(Bill)
            .filter(Bill.client_id == client_id)
            .filter(Bill.supplier_id == supplier.supplier_id)
            .filter(Bill.txn_date.between(start_date_parsed, end_date_parsed))
            .with_entities(Bill.home_total_amount)
            .all()
        )

        total_amount = sum(float(row[0]) for row in total)
        return f"Total spend on {supplier.company_name} from {start_date} to {end_date} is {total_amount:.2f}."
    except Exception as e:
        return f"Error calculating spend: {str(e)}"
    finally:
        db.close()

get_total_spend_by_supplier_tool = StructuredTool.from_function(
    func=get_total_spend_by_supplier,
    name="get_total_spend_by_supplier",
    description="Returns total spend for a given supplier (resolved from name and client) between two dates.",
    args_schema=SpendAnalyticsInput,
)
