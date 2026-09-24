# data-domain

Data contracts, schemas, mappings, and target models — owned by data
engineers. `notebooks/` holds the transformation code an AI agent drafts
against these contracts (in the sibling `agent-platform` repo); a human
reviews and merges every change via PR.

- `contracts/<entity>.yaml` — business rules (required, unique, allowed
  values, format, constraints)
- `schemas/<entity>_source.yaml` — raw source column names/types
- `mappings/<entity>.yaml` — source→target field mapping + transform/cast
- `models/<entity>.yaml` — target table shape
- `notebooks/<entity>_transformation.py` — the generated transformation code
- `data/` — synthetic seed/test data and the local DuckDB warehouse

**Full architecture, setup, and how this connects to the agent platform:**
see [`agent-platform`'s README](../agent-platform/README.md) (architecture
diagram) and [`docs/RUNBOOK.md`](../agent-platform/docs/RUNBOOK.md) (install,
setup, troubleshooting) in the sibling repo.
