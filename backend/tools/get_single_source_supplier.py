from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class SingleSourceSupplierInput(BaseModel):
    client_id: int = Field(..., description="The client ID to check for single-source suppliers")

def get_single_source_suppliers(client_id: int) -> str:
    from backend.database import SessionLocal
    from backend.models import Supplier, Bill, BillLine, Item
    from sqlalchemy import func

    db = SessionLocal()
    try:
        # Subquery this basically gets item_ids that are supplied by only one supplier for this client
        single_supplier_items = (
            db.query(
                BillLine.item_id.label("item_id")
            )
            .join(Bill, Bill.bill_id == BillLine.bill_id)
            .filter(Bill.client_id == client_id)
            .group_by(BillLine.item_id)
            .having(func.count(func.distinct(Bill.supplier_id)) == 1)
            .subquery()
        )

        #Gets item name and supplier name for those items we basically get 
        results = (
            db.query(
                Item.item_name,
                Supplier.company_name
            )
            .join(BillLine, Item.item_id == BillLine.item_id)
            .join(Bill, Bill.bill_id == BillLine.bill_id)
            .join(Supplier, Supplier.supplier_id == Bill.supplier_id)
            .join(single_supplier_items, single_supplier_items.c.item_id == Item.item_id)
            .filter(Bill.client_id == client_id)
            .group_by(Item.item_id, Supplier.company_name)
            .all()
        )

        if not results:
            return "No single-source suppliers found. All items are sourced from multiple suppliers."

        response = "Single-source suppliers and the items they exclusively supply:\n"
        for item_name, company_name in results:
            response += f"- {company_name}: {item_name}\n"
        return response

    except Exception as e:
        return f"Error checking single-source suppliers: {str(e)}"
    finally:
        db.close()

get_single_source_suppliers_tool = StructuredTool.from_function(
    func=get_single_source_suppliers,
    name="get_single_source_suppliers",
    description="Identifies suppliers that are the only source for specific items (single-source suppliers) for a given client.",
    args_schema=SingleSourceSupplierInput,
)
