"""Generate synthetic customer source data for the data-agent-platform POC.

Produces data/raw/customers.csv with mostly-valid rows plus a deliberate
set of problematic rows (each tagged in a comment below) to exercise
data-quality validation later in the pipeline.
"""
import csv
import random
from datetime import date, timedelta

random.seed(42)

FIRST_NAMES = ["John", "Jane", "Alice", "Bob", "Maria", "Wei", "Fatima", "Liam",
               "Olivia", "Noah", "Emma", "Lucas", "Sophia", "Mateo", "Aisha",
               "Ivan", "Priya", "Carlos", "Yuki", "Grace"]
LAST_NAMES = ["Smith", "Johnson", "Garcia", "Chen", "Khan", "Müller", "Silva",
              "Kowalski", "Rossi", "Tanaka", "Nguyen", "Kumar", "Dubois",
              "Andersson", "Costa", "Novak", "Haddad", "Petrov", "Lindgren", "Okafor"]
COUNTRIES = ["US", "CA", "GB", "DE", "FR", "IN", "BR", "JP", "AU", "NG"]
STATUSES = ["active", "inactive", "pending"]

rows = []

def random_dob():
    start = date(1955, 1, 1)
    end = date(2005, 12, 31)
    delta_days = (end - start).days
    return (start + timedelta(days=random.randint(0, delta_days))).isoformat()

def random_signup():
    start = date(2019, 1, 1)
    end = date(2025, 12, 31)
    delta_days = (end - start).days
    return (start + timedelta(days=random.randint(0, delta_days))).isoformat()

# --- Valid rows ---
for i in range(1, 23):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    cid = f"CUST{i:04d}"
    rows.append({
        "customer_id": cid,
        "first_name": first,
        "last_name": last,
        "dob": random_dob(),
        "email": f"{first.lower()}.{last.lower()}{i}@example.com",
        "country": random.choice(COUNTRIES),
        "signup_date": random_signup(),
        "status": random.choice(STATUSES),
    })

# --- Problematic rows (intentional, for data-quality validation) ---

# 1. Missing dob
rows.append({
    "customer_id": "CUST0023", "first_name": "Nina", "last_name": "Petrov",
    "dob": "", "email": "nina.petrov@example.com", "country": "GB",
    "signup_date": random_signup(), "status": "active",
})

# 2. Malformed dob (wrong format, not ISO)
rows.append({
    "customer_id": "CUST0024", "first_name": "Tomás", "last_name": "Silva",
    "dob": "14/03/1985", "email": "tomas.silva@example.com", "country": "BR",
    "signup_date": random_signup(), "status": "active",
})

# 3. Missing email
rows.append({
    "customer_id": "CUST0025", "first_name": "Grace", "last_name": "Okafor",
    "dob": random_dob(), "email": "", "country": "NG",
    "signup_date": random_signup(), "status": "pending",
})

# 4. Malformed email (no @)
rows.append({
    "customer_id": "CUST0026", "first_name": "Ivan", "last_name": "Novak",
    "dob": random_dob(), "email": "ivan.novak_example.com", "country": "DE",
    "signup_date": random_signup(), "status": "active",
})

# 5. Duplicate customer_id (reuses CUST0001)
rows.append({
    "customer_id": "CUST0001", "first_name": "Duplicate", "last_name": "Entry",
    "dob": random_dob(), "email": "duplicate.entry@example.com", "country": "US",
    "signup_date": random_signup(), "status": "active",
})

# 6. Invalid status value
rows.append({
    "customer_id": "CUST0027", "first_name": "Priya", "last_name": "Kumar",
    "dob": random_dob(), "email": "priya.kumar@example.com", "country": "IN",
    "signup_date": random_signup(), "status": "unknown_status",
})

# 7. Invalid country code
rows.append({
    "customer_id": "CUST0028", "first_name": "Yuki", "last_name": "Tanaka",
    "dob": random_dob(), "email": "yuki.tanaka@example.com", "country": "ZZ9",
    "signup_date": random_signup(), "status": "active",
})

# 8. Future signup_date
rows.append({
    "customer_id": "CUST0029", "first_name": "Liam", "last_name": "Andersson",
    "dob": random_dob(), "email": "liam.andersson@example.com", "country": "CA",
    "signup_date": "2099-01-01", "status": "active",
})

fieldnames = ["customer_id", "first_name", "last_name", "dob", "email",
              "country", "signup_date", "status"]

with open("data/raw/customers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to data/raw/customers.csv")
