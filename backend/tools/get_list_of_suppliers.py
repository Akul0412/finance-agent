from pydantic import BaseModel, Field

class EmptyInput(BaseModel):
    client_id: str = Field(..., description="This parameter tells us which client currently wants the list of their suppliers.")

def get_list_of_suppliers(client_id: str):
    from backend.database import SessionLocal
    from backend.models import Supplier

    db = SessionLocal()

    try:
        print("DEBUG: Opening DB session...")
        print(f"DEBUG: Fetching suppliers for client_id = {client_id}...")
        
        suppliers = db.query(Supplier.company_name).filter(Supplier.client_id == client_id).all()
        print(f"DEBUG: Raw suppliers query result = {suppliers}")

        if not suppliers:
            return f"No suppliers found in the database for client_id = {client_id}."
        
        import json
        supplier_names = [row[0] for row in suppliers]
        return json.dumps({"supplier_names": supplier_names})
    
    except Exception as e:
        return f"Error found while fetching suppliers: {str(e)}"
    finally:
        db.close()


from langchain.tools import StructuredTool

get_list_of_suppliers_tool = StructuredTool.from_function(
    func=get_list_of_suppliers,
    name="get_list_of_suppliers",
    description="Returns a list of supplier company names for a given client_id. Use this tool to answer any question where the user asks about the list of suppliers for a client.",
    args_schema=EmptyInput,
)
