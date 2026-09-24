"""Load synthetic product CSV into a local DuckDB database (POC substitute for Databricks).

Unlike raw_customers (a legacy naming exception - see docs/RUNBOOK.md), this
table is named to match the entity exactly: "product", not "raw_products" -
so source_table is always just the entity name for anything added from here on.
"""
import duckdb

con = duckdb.connect("data/warehouse.duckdb")

con.execute("""
    CREATE OR REPLACE TABLE product AS
    SELECT * FROM read_csv_auto('data/raw/products.csv', ALL_VARCHAR=TRUE)
""")

count = con.execute("SELECT COUNT(*) FROM product").fetchone()[0]
print(f"Loaded {count} rows into product (data/warehouse.duckdb)")

con.close()
