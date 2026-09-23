import duckdb

con = duckdb.connect("data/warehouse.duckdb")

con.execute("""
CREATE OR REPLACE TABLE customer_target AS
SELECT
    CAST(customer_id AS VARCHAR) AS customer_id,
    CAST(first_name AS VARCHAR) AS first_name,
    CAST(last_name AS VARCHAR) AS last_name,
    TRY_CAST(dob AS DATE) AS birth_date,
    CAST(LOWER(email) AS VARCHAR) AS email,
    CAST(country AS VARCHAR) AS country,
    TRY_CAST(signup_date AS DATE) AS signup_date,
    CAST(status AS VARCHAR) AS status
FROM raw_customers
""")

con.close()