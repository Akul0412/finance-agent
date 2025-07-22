CREATE DATABASE IF NOT EXISTS fintech_analytics;
USE fintech_analytics;

CREATE TABLE Supplier (
    supplier_id VARCHAR(45) PRIMARY KEY,
    client_id INT,
    company_name VARCHAR(500),
    currency_code CHAR(3),
    active_status INT,
    type INT,
    created_time DATETIME,
    updated_time DATETIME,
    tax_id VARCHAR(45)
);

CREATE TABLE Bill (
    bill_id VARCHAR(45) PRIMARY KEY,
    client_id INT,
    supplier_id VARCHAR(45),
    txn_total_amount DECIMAL(21,6),
    txn_date DATE,
    currency_code CHAR(3),
    exchange_rate DECIMAL(19, 6),
    home_total_amount DECIMAL(21, 6),
    payment_status INT,
    active_status INT,
    created_time DATETIME,
    due_date DATE,
    description VARCHAR(4096),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);

CREATE TABLE Item (
    item_id VARCHAR(45) PRIMARY KEY,
    client_id INT,
    item_name VARCHAR(255),
    full_name VARCHAR(1024),
    item_type VARCHAR(45),
    purchase_cost DECIMAL(21, 6),
    unit_price DECIMAL(21, 6),
    active_status INT
);

CREATE TABLE Bill_Line (
    line_id VARCHAR(45) PRIMARY KEY,
    client_id INT,
    bill_id VARCHAR(45),
    item_id VARCHAR(45),
    account_id VARCHAR(45),
    description VARCHAR(4096),
    amount DECIMAL(21, 6),
    quality DECIMAL(21,6),
    unit_price DECIMAL(21, 6),
    billable TINYINT(1),
    FOREIGN KEY (bill_id) REFERENCES Bill(bill_id),
    FOREIGN KEY (item_id) REFERENCES Item(item_id)
);

CREATE TABLE Payment (
    payment_id VARCHAR(45) PRIMARY KEY,
    client_id INT,
    txn_total_amount DECIMAL(19, 4),
    home_total_amount DECIMAL(19, 4),
    txn_date DATE,
    currency_code CHAR(3),
    exchange_rate DECIMAL(19, 6),
    active_status INT,
    void_status TINYINT(1)
);

