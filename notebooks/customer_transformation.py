"""
Customer transformation notebook.

Reads the raw `raw_customers` source table and produces the curated
`customer_target` table defined in models/customer.yaml, following the
field mapping in mappings/customer.yaml and enforcing the rules in
contracts/customer.yaml.

Source -> target field renames (see mappings/customer.yaml):
    dob -> birth_date (cast to DATE)
    email -> email (lowercased)
    signup_date -> signup_date (cast to DATE)
All other fields pass through unchanged (customer_id, first_name,
last_name, country, status).
"""

import duckdb

con = duckdb.connect("data/warehouse.duckdb")

con.execute("""
CREATE OR REPLACE TABLE customer_target AS
-- Step 1: tag every raw row with a stable ordering key (src_seq) so that,
-- if duplicate customer_ids show up later, we can deterministically pick
-- which row "wins" instead of relying on incidental table order.
WITH numbered AS (
    SELECT
        *,
        ROW_NUMBER() OVER () AS src_seq
    FROM raw_customers
),
-- Step 2: apply the field mapping from mappings/customer.yaml -
-- cast/rename source columns to their target names and types.
mapped AS (
    SELECT
        CAST(customer_id AS VARCHAR) AS customer_id,
        CAST(first_name AS VARCHAR) AS first_name,
        CAST(last_name AS VARCHAR) AS last_name,
        -- dob -> birth_date: raw dates arrive in inconsistent formats, so
        -- try a plain cast first, then fall back through a list of known
        -- formats via TRY_STRPTIME. COALESCE keeps the first one that
        -- parses; unparseable values end up NULL and get filtered out
        -- below (contract requires birth_date to be present).
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
        -- email: contract requires a valid email format; mapping specifies
        -- a "lowercase" transform so downstream comparisons/joins are
        -- case-insensitive.
        LOWER(CAST(email AS VARCHAR)) AS email,
        CAST(country AS VARCHAR) AS country,
        -- signup_date: same multi-format date parsing strategy as dob
        -- above, since the raw source is not consistently formatted.
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
-- Step 3: enforce contracts/customer.yaml requirements - drop any row
-- that fails a required/format/allowed-values/constraint rule rather
-- than let bad data reach the curated target table.
valid AS (
    SELECT *
    FROM mapped
    WHERE customer_id IS NOT NULL                                   -- required, unique
      AND birth_date IS NOT NULL                                    -- required valid date
      AND email IS NOT NULL
      AND REGEXP_MATCHES(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')  -- format: email
      AND status IN ('active', 'inactive', 'pending')                -- allowed_values
      AND country IS NOT NULL
      AND REGEXP_MATCHES(country, '^[A-Z]{2}$')                      -- format: iso_country_code_2
      AND signup_date IS NOT NULL
      AND signup_date <= CURRENT_DATE                                -- constraint: not_in_future
),
-- Step 4: contract requires customer_id to be unique. If the source ever
-- contains duplicate customer_ids, keep only the earliest-seen row
-- (by src_seq) per customer_id and drop the rest.
deduped AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY src_seq) AS dedup_rank
    FROM valid
)
-- Final projection: emit exactly the columns defined in
-- models/customer.yaml, in order, for the curated customer_target table.
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
