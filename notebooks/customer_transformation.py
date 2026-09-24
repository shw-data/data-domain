import duckdb

con = duckdb.connect("data/warehouse.duckdb")

con.execute("""
CREATE OR REPLACE TABLE customer_target AS
WITH numbered AS (
    SELECT
        *,
        ROW_NUMBER() OVER () AS src_seq
    FROM raw_customers
),
mapped AS (
    SELECT
        CAST(customer_id AS VARCHAR) AS customer_id,
        CAST(first_name AS VARCHAR) AS first_name,
        CAST(last_name AS VARCHAR) AS last_name,
        COALESCE(
            TRY_CAST(dob AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(dob AS VARCHAR), '%Y-%m-%d') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(dob AS VARCHAR), '%d/%m/%Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(dob AS VARCHAR), '%m/%d/%Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(dob AS VARCHAR), '%d-%m-%Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(dob AS VARCHAR), '%Y/%m/%d') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(dob AS VARCHAR), '%d.%m.%Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(dob AS VARCHAR), '%Y%m%d') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(dob AS VARCHAR), '%B %d, %Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(dob AS VARCHAR), '%b %d, %Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(dob AS VARCHAR), '%d %B %Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(dob AS VARCHAR), '%d %b %Y') AS DATE)
        ) AS birth_date,
        LOWER(CAST(email AS VARCHAR)) AS email,
        CAST(country AS VARCHAR) AS country,
        COALESCE(
            TRY_CAST(signup_date AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(signup_date AS VARCHAR), '%Y-%m-%d') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(signup_date AS VARCHAR), '%d/%m/%Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(signup_date AS VARCHAR), '%m/%d/%Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(signup_date AS VARCHAR), '%d-%m-%Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(signup_date AS VARCHAR), '%Y/%m/%d') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(signup_date AS VARCHAR), '%d.%m.%Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(signup_date AS VARCHAR), '%Y%m%d') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(signup_date AS VARCHAR), '%B %d, %Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(signup_date AS VARCHAR), '%b %d, %Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(signup_date AS VARCHAR), '%d %B %Y') AS DATE),
            TRY_CAST(TRY_STRPTIME(CAST(signup_date AS VARCHAR), '%d %b %Y') AS DATE)
        ) AS signup_date,
        CAST(status AS VARCHAR) AS status,
        src_seq
    FROM numbered
),
valid AS (
    SELECT *
    FROM mapped
    WHERE customer_id IS NOT NULL
      AND birth_date IS NOT NULL
      AND email IS NOT NULL
      AND REGEXP_MATCHES(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
      AND status IN ('active', 'inactive', 'pending')
      AND country IS NOT NULL
      AND REGEXP_MATCHES(country, '^[A-Z]{2}$')
      AND signup_date IS NOT NULL
      AND signup_date <= CURRENT_DATE
),
deduped AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY src_seq) AS dedup_rank
    FROM valid
)
SELECT
    customer_id,
    first_name,
    last_name,
    birth_date,
    email,
    country,
    signup_date,
    status
FROM deduped
WHERE dedup_rank = 1
""")

con.close()