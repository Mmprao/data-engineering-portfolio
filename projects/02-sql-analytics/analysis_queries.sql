-- 1. Revenue and order count by state (completed orders only).
SELECT
    c.state_code,
    COUNT(*) AS completed_orders,
    SUM(o.order_amount) AS total_revenue
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
WHERE o.order_status = 'Completed'
GROUP BY c.state_code
ORDER BY total_revenue DESC;

-- 2. Customer-level order summary, including customers with no orders.
SELECT
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS order_count,
    COALESCE(SUM(o.order_amount), 0) AS lifetime_order_value
FROM customers AS c
LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id
   AND o.order_status = 'Completed'
GROUP BY c.customer_id, c.customer_name
ORDER BY lifetime_order_value DESC;

-- 3. Rank customers by completed spend within each state.
WITH customer_spend AS (
    SELECT
        c.state_code,
        c.customer_id,
        c.customer_name,
        SUM(o.order_amount) AS total_spend
    FROM customers AS c
    JOIN orders AS o ON o.customer_id = c.customer_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.state_code, c.customer_id, c.customer_name
)
SELECT
    state_code,
    customer_name,
    total_spend,
    DENSE_RANK() OVER (
        PARTITION BY state_code
        ORDER BY total_spend DESC
    ) AS spend_rank
FROM customer_spend;

-- 4. Running completed revenue by order date.
SELECT
    order_date,
    order_id,
    order_amount,
    SUM(order_amount) OVER (
        ORDER BY order_date, order_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_revenue
FROM orders
WHERE order_status = 'Completed';

-- 5. Basic data quality checks.
SELECT COUNT(*) AS negative_or_zero_amounts
FROM orders
WHERE order_amount <= 0;

SELECT customer_id, COUNT(*) AS duplicate_customer_rows
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;
