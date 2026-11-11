-- Gold-layer daily sales summary.
-- Assumes the Silver layer is exposed as a table named silver_orders.

SELECT
    order_date,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(quantity) AS units_sold,
    CAST(SUM(total) AS DECIMAL(18, 2)) AS revenue
FROM silver_orders
GROUP BY order_date
ORDER BY order_date;
