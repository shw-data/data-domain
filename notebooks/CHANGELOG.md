# Notebooks changelog

All notable changes to files under `notebooks/` are documented here.

## customer

### 2026-09-24
- Added explanatory comments to `customer_transformation.py` (module
  docstring plus inline comments on each CTE step: numbering/dedup key,
  field mapping per `mappings/customer.yaml`, contract-rule filtering per
  `contracts/customer.yaml`, and the final projection matching
  `models/customer.yaml`). No transformation logic changed;
  `run_validation("customer", "raw_customers")` still passes with no
  errors.
