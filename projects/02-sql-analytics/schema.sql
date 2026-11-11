-- Fictional retail dataset for portfolio practice.
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    state_code CHAR(2)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    order_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

INSERT INTO customers (customer_id, customer_name, state_code) VALUES
(1, 'Ava Patel', 'NJ'),
(2, 'Jordan Lee', 'NY'),
(3, 'Sam Rivera', 'FL'),
(4, 'Taylor Kim', 'TX');

INSERT INTO orders (order_id, customer_id, order_date, order_status, order_amount) VALUES
(2001, 1, '2026-10-01', 'Completed', 120.00),
(2002, 2, '2026-10-02', 'Completed', 75.50),
(2003, 1, '2026-10-05', 'Pending', 45.00),
(2004, 3, '2026-10-06', 'Completed', 210.25),
(2005, 4, '2026-10-07', 'Cancelled', 30.00),
(2006, 2, '2026-10-09', 'Completed', 99.99),
(2007, 3, '2026-10-10', 'Completed', 80.00);
