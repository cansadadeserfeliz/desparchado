---
name: Test file location by layer
description: Service tests go in tests/services/test_<module>.py, not directly in tests/
type: feedback
---

Place tests in a subdirectory matching the layer of the code under test:

- `<app>/tests/services/test_<module>.py` for service functions
- `<app>/tests/views/test_<module>.py` for views (already the convention in dashboard/)

**Why:** User moved `dashboard/tests/test_filbo_service.py` → `dashboard/tests/services/test_filbo.py`. Keeping service tests grouped under `tests/services/` mirrors the `services/` source layout and avoids a flat `tests/` directory.

**How to apply:** When writing tests for any service module (e.g. `dashboard/services/filbo.py`), create the file at `dashboard/tests/services/test_filbo.py`. Always create an `__init__.py` in the new subdirectory. Apply the same pattern for other layers (forms, models, etc.) if a `tests/<layer>/` directory already exists or the user establishes one.
