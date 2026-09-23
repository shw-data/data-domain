import duckdb

con = duckdb.connect("data/warehouse.duckdb")


def show(title, sql):
    print(f"\n=== {title} ===")
    result = con.execute(sql)
    cols = [d[0] for d in result.description]
    rows = result.fetchall()
    print(" | ".join(cols))
    for row in rows:
        print(" | ".join(str(v) for v in row))
    print(f"({len(rows)} row(s))")


show("Row count", "SELECT COUNT(*) AS total_rows FROM raw_customers")

show("Sample valid rows", """
    SELECT customer_id, first_name, last_name, dob, email, country, signup_date, status
    FROM raw_customers
    LIMIT 5
""")

show("Rows with missing dob or email", """
    SELECT customer_id, dob, email
    FROM raw_customers
    WHERE dob IS NULL OR dob = '' OR email IS NULL OR email = ''
""")

show("Rows with malformed email (no '@')", """
    SELECT customer_id, email
    FROM raw_customers
    WHERE email IS NOT NULL AND email != '' AND email NOT LIKE '%@%'
""")

show("Duplicate customer_id values", """
    SELECT customer_id, COUNT(*) AS n
    FROM raw_customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
""")

show("Invalid status values", """
    SELECT customer_id, status
    FROM raw_customers
    WHERE status NOT IN ('active', 'inactive', 'pending')
""")

show("Future signup_date", """
    SELECT customer_id, signup_date
    FROM raw_customers
    WHERE signup_date > CAST(current_date AS VARCHAR)
""")

con.close()
