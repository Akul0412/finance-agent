# 📘 Knowledge Base: Supplier Analytics Schema

## 🧱 Overview

This schema supports a **supplier analytics** system that tracks transactions (bills, payments), supplier metadata, and itemized billing. It enables use cases like:

- Total/average spend analysis
- Frequent or high-risk supplier identification
- Item-level purchase breakdown
- Overdue payment tracking
- Supplier activity by client

---

## 📦 Table: `Supplier`

Stores metadata for each supplier used by a client.

| Column         | Type         | Description                                      |
|----------------|--------------|--------------------------------------------------|
| `supplier_id`  | String(45)   | Unique identifier for the supplier              |
| `client_id`    | Integer      | ID of the client associated with this supplier  |
| `company_name` | String(500)  | Name of the supplier's company                  |
| `currency_code`| CHAR(3)      | Currency used by the supplier (e.g., USD)       |
| `active_status`| Integer      | 1 = active, 0 = inactive                         |
| `type`         | Integer      | Type of supplier (e.g., manufacturer = 1)       |
| `created_time` | DateTime     | When the supplier was added                     |
| `updated_time` | DateTime     | When the supplier info was last updated         |
| `tax_id`       | String(45)   | Tax registration ID                             |

**Relationships:**  
- Referenced in `Bill.supplier_id`

---

## 🧾 Table: `Bill`

Represents a bill issued by a supplier to a client.

| Column             | Type             | Description                                           |
|--------------------|------------------|-------------------------------------------------------|
| `bill_id`          | String(45)       | Unique ID of the bill                                 |
| `client_id`        | Integer          | Client receiving the bill                             |
| `supplier_id`      | String(45)       | FK to `Supplier.supplier_id`                          |
| `txn_total_amount` | DECIMAL(21, 6)   | Total in bill currency                                |
| `txn_date`         | DateTime         | Transaction date                                      |
| `currency_code`    | CHAR(3)          | Bill currency                                         |
| `exchange_rate`    | DECIMAL(19, 6)   | FX rate to convert to home currency                   |
| `home_total_amount`| DECIMAL(21, 6)   | Amount in home currency                               |
| `payment_status`   | Integer          | 0 = unpaid, 1 = partial, 2 = paid                     |
| `active_status`    | Integer          | 1 = active, 0 = voided                                |
| `created_time`     | DateTime         | Bill creation time                                    |
| `due_date`         | DateTime         | Payment deadline                                      |
| `description`      | String(4096)     | Optional bill notes or context                        |

**Relationships:**  
- References `Supplier`  
- Referenced in `Bill_Line.bill_id`

---

## 📄 Table: `Bill_Line`

Line items within a bill.

| Column        | Type             | Description                                     |
|---------------|------------------|-------------------------------------------------|
| `line_id`     | String(45)       | Unique identifier of the line item              |
| `client_id`   | Integer          | Client ID                                       |
| `bill_id`     | String(45)       | FK to `Bill.bill_id`                            |
| `item_id`     | String(45)       | FK to `Item.item_id`                            |
| `account_id`  | String(45)       | Optional accounting code                        |
| `description` | String(4096)     | Description of service/product                  |
| `amount`      | DECIMAL(21, 6)   | Line total = `quality` × `unit_price`           |
| `quality`     | DECIMAL(21, 6)   | Quantity of item                                |
| `unit_price`  | DECIMAL(21, 6)   | Price per unit                                  |
| `billable`    | Boolean          | If True, the item is chargeable                 |

**Relationships:**  
- References `Bill`, `Item`

---

## 📋 Table: `Item`

Defines the catalog of products/services.

| Column         | Type             | Description                           |
|----------------|------------------|---------------------------------------|
| `item_id`      | String(45)       | Unique identifier                     |
| `client_id`    | Integer          | Client owning the item                |
| `item_name`    | String(255)      | Short name of the item                |
| `full_name`    | String(1024)     | Full name or description              |
| `item_type`    | String(45)       | Category or type (e.g., service)      |
| `purchase_cost`| DECIMAL(21, 6)   | Cost to acquire                       |
| `unit_price`   | DECIMAL(21, 6)   | Default price per unit                |
| `active_status`| Integer          | 1 = active, 0 = deprecated             |

**Relationships:**  
- Referenced in `Bill_Line.item_id`

---

## 💰 Table: `Payment`

Represents payments made by clients to suppliers.

| Column             | Type             | Description                                      |
|--------------------|------------------|--------------------------------------------------|
| `payment_id`       | String(45)       | Unique identifier for the payment                |
| `client_id`        | Integer          | ID of the paying client                          |
| `txn_total_amount` | DECIMAL(19, 4)   | Amount in payment currency                       |
| `home_total_amount`| DECIMAL(19, 4)   | Converted to home currency                       |
| `txn_date`         | DateTime         | When payment was made                            |
| `currency_code`    | CHAR(3)          | Currency used for transaction                    |
| `exchange_rate`    | DECIMAL(19, 6)   | FX rate                                          |
| `active_status`    | Integer          | 1 = valid, 0 = deleted                           |
| `void_status`      | Boolean          | True if the payment was voided                   |

---

## 🧭 Relationships Summary

- **`Supplier` → `Bill`**: A supplier can issue many bills.
- **`Bill` → `Bill_Line`**: Each bill can contain multiple line items.
- **`Item` → `Bill_Line`**: Items are used in many bill lines.
- **`Payment`**: Independent records, could be associated to `Bill` using `client_id`, `txn_date`, or extended join logic.

---

## ✅ Usage Scenarios

- **Total spend per supplier**: Join `Bill` grouped by `supplier_id`
- **Top purchased items**: Join `Bill_Line` + `Item`, group by `item_name`
- **Supplier frequency**: Count number of `Bill` per `supplier_id`
- **Outstanding payments**: Filter `Bill` where `payment_status != 2`
- **Void tracking**: Use `Payment.void_status` and `Bill.active_status`
