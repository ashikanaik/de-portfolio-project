WITH source AS (
    SELECT * FROM raw.products
),
cleaned AS (
    SELECT
        product_id,
        product_category_name       AS category,
        product_name_lenght         AS name_length,
        product_description_lenght  AS description_length,
        product_photos_qty          AS photos_count,
        product_weight_g            AS weight_grams,
        product_length_cm           AS length_cm,
        product_height_cm           AS height_cm,
        product_width_cm            AS width_cm
    FROM source
    WHERE product_id IS NOT NULL
)
SELECT * FROM cleaned