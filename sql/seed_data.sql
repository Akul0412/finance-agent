USE fintech_analytics;

-- Clear old data first (optional)
DELETE FROM Bill_Line;
DELETE FROM Bill;
DELETE FROM Item;
DELETE FROM Supplier;

-- Suppliers
INSERT INTO Supplier (supplier_id, client_id, company_name, currency_code, active_status, type, created_time, updated_time, tax_id)
VALUES 
('sup1', 1, 'Alpha Corp', 'USD', 1, 2, NOW(), NOW(), 'TAX123'),
('sup2', 1, 'Beta LLC', 'EUR', 1, 1, NOW(), NOW(), 'TAX456');

-- Items
INSERT INTO Item (item_id, client_id, item_name, full_name, item_type, purchase_cost, unit_price, active_status)
VALUES 
('itm1', 1, 'Widget A', 'Alpha Widget A', 'Product', 10.00, 15.00, 1),
('itm2', 1, 'Gadget B', 'Beta Gadget B', 'Product', 20.00, 30.00, 1);

-- Bills
INSERT INTO Bill (bill_id, client_id, supplier_id, txn_total_amount, txn_date, currency_code, exchange_rate, home_total_amount, payment_status, active_status, created_time, due_date, description)
VALUES 
('bill1', 1, 'sup1', 150.00, '2024-05-01', 'USD', 1.0, 150.00, 1, 1, NOW(), '2024-06-01', 'Bill for Widgets'),
('bill2', 1, 'sup2', 200.00, '2024-05-03', 'EUR', 1.1, 220.00, 0, 1, NOW(), '2024-06-03', 'Bill for Gadgets');

-- Bill Lines
INSERT INTO Bill_Line (line_id, client_id, bill_id, item_id, account_id, description, amount, quality, unit_price, billable)
VALUES 
('line1', 1, 'bill1', 'itm1', 'acc1', 'Widget A x10', 150.00, 10, 15.00, 1),
('line2', 1, 'bill2', 'itm2', 'acc2', 'Gadget B x5', 150.00, 5, 30.00, 1);
