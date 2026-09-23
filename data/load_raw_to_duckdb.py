"""Load synthetic customer CSV into a local DuckDB database (POC substitute for Databricks)."""
import duckdb

con = duckdb.connect("data/warehouse.duckdb")

con.execute("""
    CREATE OR REPLACE TABLE raw_customers AS
    SELECT * FROM read_csv_auto('data/raw/customers.csv', ALL_VARCHAR=TRUE)
""")

count = con.execute("SELECT COUNT(*) FROM raw_customers").fetchone()[0]
print(f"Loaded {count} rows into raw_customers (data/warehouse.duckdb)")

con.close()
