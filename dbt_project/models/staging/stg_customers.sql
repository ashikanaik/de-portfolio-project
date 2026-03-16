WITH source AS (
    SELECT * FROM raw.customers
),
cleaned AS (
    SELECT
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix    AS zip_code,
        customer_city               AS city,
        customer_state              AS state
    FROM source
    WHERE customer_id IS NOT NULL
)
SELECT * FROM cleaned