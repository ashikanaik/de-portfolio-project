WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),
payments AS (
    SELECT * FROM {{ ref('stg_payments') }}
),
orders_with_location AS (
    SELECT
        o.order_id,
        o.purchased_at,
        o.order_status,
        c.city,
        c.state
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
),
orders_with_revenue AS (
    SELECT
        ol.order_id,
        ol.purchased_at,
        ol.order_status,
        ol.city,
        ol.state,
        SUM(p.payment_value) AS order_value
    FROM orders_with_location ol
    JOIN payments p ON ol.order_id = p.order_id
    GROUP BY
        ol.order_id,
        ol.purchased_at,
        ol.order_status,
        ol.city,
        ol.state
),
final AS (
    SELECT
        city,
        state,
        STRFTIME(purchased_at, '%Y-%m')     AS month,
        COUNT(DISTINCT order_id)            AS total_orders,
        ROUND(SUM(order_value), 2)          AS total_revenue,
        ROUND(AVG(order_value), 2)          AS avg_order_value
    FROM orders_with_revenue
    WHERE order_status != 'cancelled'
    GROUP BY city, state, month
    ORDER BY month DESC, total_revenue DESC
)
SELECT * FROM final