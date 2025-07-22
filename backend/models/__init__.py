from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, ForeignKey, Text, CHAR, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Supplier(Base):
    __tablename__ = 'Supplier'

    supplier_id = Column(String(45), primary_key=True)
    client_id = Column(Integer)
    company_name = Column(String(500))
    currency_code = Column(CHAR(3))
    active_status = Column(Integer)
    type = Column(Integer)
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    tax_id = Column(String(45))

class Bill(Base):
    __tablename__ = 'Bill'

    bill_id = Column(String(45), primary_key=True)
    client_id = Column(Integer)
    supplier_id = Column(String(45), ForeignKey('Supplier.supplier_id'))
    txn_total_amount = Column(DECIMAL(21, 6))
    txn_date = Column(DateTime)
    currency_code = Column(CHAR(3))
    exchange_rate = Column(DECIMAL(19, 6))
    home_total_amount = Column(DECIMAL(21, 6))
    payment_status = Column(Integer)
    active_status = Column(Integer)
    created_time = Column(DateTime)
    due_date = Column(DateTime)
    description = Column(String(4096))

class Item(Base):
    __tablename__ = 'Item'

    item_id = Column(String(45), primary_key=True)
    client_id = Column(Integer)
    item_name = Column(String(255))
    full_name = Column(String(1024))
    item_type = Column(String(45))
    purchase_cost = Column(DECIMAL(21, 6))
    unit_price = Column(DECIMAL(21, 6))
    active_status = Column(Integer)

class BillLine(Base):
    __tablename__ = 'Bill_Line'

    line_id = Column(String(45), primary_key=True)
    client_id = Column(Integer)
    bill_id = Column(String(45), ForeignKey('Bill.bill_id'))
    item_id = Column(String(45), ForeignKey('Item.item_id'))
    account_id = Column(String(45))
    description = Column(String(4096))
    amount = Column(DECIMAL(21, 6))
    quality = Column(DECIMAL(21, 6))
    unit_price = Column(DECIMAL(21, 6))
    billable = Column(Boolean)

class Payment(Base):
    __tablename__ = 'Payment'

    payment_id = Column(String(45), primary_key=True)
    client_id = Column(Integer)
    txn_total_amount = Column(DECIMAL(19, 4))
    home_total_amount = Column(DECIMAL(19, 4))
    txn_date = Column(DateTime)
    currency_code = Column(CHAR(3))
    exchange_rate = Column(DECIMAL(19, 6))
    active_status = Column(Integer)
    void_status = Column(Boolean)