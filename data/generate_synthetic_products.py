"""Generate synthetic product source data for the data-agent-platform POC.

Mirrors generate_synthetic_customers.py: mostly-valid rows plus a small set
of deliberately problematic ones, to exercise the product contract's own
validation rules (required, unique, allowed_values, not_in_future).
"""
import csv
import random
from datetime import date, timedelta

random.seed(11)

STATUSES = ["active", "discontinued", "draft"]
CATEGORIES = ["widget", "gadget", "gizmo", "doohickey"]

rows = []

def random_launch_date():
    start = date(2022, 1, 1)
    end = date(2025, 12, 31)
    delta_days = (end - start).days
    return (start + timedelta(days=random.randint(0, delta_days))).isoformat()

# --- Valid rows ---
for i in range(1, 16):
    cat = random.choice(CATEGORIES)
    rows.append({
        "product_id": f"PROD{i:04d}",
        "sku": f"{cat.upper()[:3]}-{i:04d}",
        "launch_date": random_launch_date(),
        "price": round(random.uniform(5, 200), 2),
        "status": random.choice(STATUSES),
    })

# --- Problematic rows (intentional, for data-quality validation) ---

# 1. Missing sku
rows.append({
    "product_id": "PROD0016", "sku": "", "launch_date": random_launch_date(),
    "price": 29.99, "status": "active",
})

# 2. Duplicate product_id (reuses PROD0001)
rows.append({
    "product_id": "PROD0001", "sku": "DUP-0001", "launch_date": random_launch_date(),
    "price": 15.00, "status": "active",
})

# 3. Invalid status value
rows.append({
    "product_id": "PROD0017", "sku": "GIZ-0017", "launch_date": random_launch_date(),
    "price": 42.00, "status": "unknown_status",
})

# 4. Future launch_date
rows.append({
    "product_id": "PROD0018", "sku": "WID-0018", "launch_date": "2099-01-01",
    "price": 75.25, "status": "draft",
})

# 5. Missing price
rows.append({
    "product_id": "PROD0019", "sku": "DOO-0019", "launch_date": random_launch_date(),
    "price": "", "status": "discontinued",
})

fieldnames = ["product_id", "sku", "launch_date", "price", "status"]

with open("data/raw/products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to data/raw/products.csv")
