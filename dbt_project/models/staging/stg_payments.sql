WITH source AS (
    SELECT * FROM raw.payments
),
cleaned AS (
    SELECT
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        payment_value
    FROM source
    WHERE order_id      IS NOT NULL
      AND payment_value  > 0
)
SELECT * FROM cleaned