WITH source AS (
    SELECT * FROM raw.orders
),
cleaned AS (
    SELECT
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp        AS purchased_at,
        order_approved_at               AS approved_at,
        order_delivered_customer_date   AS delivered_at,
        order_estimated_delivery_date   AS estimated_delivery_at
    FROM source
    WHERE order_id    IS NOT NULL
      AND customer_id IS NOT NULL
)
SELECT * FROM cleaned