---
title: 'Event target_audience field + FILBo sync'
type: 'feature'
created: '2026-04-07'
status: 'done'
baseline_commit: 'b604fa6c155fb025066e86c313e48c3d320968ad'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The FILBo spreadsheet column F carries audience segmentation data that is silently dropped during sync; there is no field on `Event` to store it, so the information is permanently lost.

**Approach:** Add an optional `target_audience` CharField with universal `TextChoices` to `Event` (not FILBo-specific), generate the migration, and update `sync_filbo_event` to read column F, translate FILBo-specific values to the universal keys, and write the field on every sync.

## Boundaries & Constraints

**Always:**
- The field is optional (`blank=True`, no default) — existing events are unaffected.
- Choices are universal and not FILBo-specific: `early_childhood`, `children`, `young_adult`, `adults`, `families`, `professionals`, `all_audiences`.
- Column F translation in the sync service uses an explicit mapping dict; FILBo's `age_13_27` and `young_adult` both map to `young_adult`, and `book_professionals` maps to `professionals`.
- Unknown or empty column-F values result in `target_audience=''` (blank); a warning is logged for non-empty unrecognized values.
- `target_audience` must be included in the `defaults` dict passed to `update_or_create` so it is kept current on every sync run.
- Labels use Spanish (consistent with other `Event` choices).

**Ask First:** None anticipated.

**Never:**
- Do not rename or reorder existing `TargetAudience` choice values once defined.
- Do not expose `target_audience` in any public-facing template or API — out of scope.
- Do not add `target_audience` to `EventFactory` defaults; leave it absent so existing tests are unaffected.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Recognized age value | Column F = `age_under_6` | `event.target_audience == 'early_childhood'` | N/A |
| `age_13_27` | Column F = `age_13_27` | `event.target_audience == 'young_adult'` | N/A |
| `young_adult` | Column F = `young_adult` | `event.target_audience == 'young_adult'` | N/A |
| `book_professionals` | Column F = `book_professionals` | `event.target_audience == 'professionals'` | N/A |
| Empty cell | Column F = `''` | `event.target_audience == ''` | N/A |
| Unknown value | Column F = `unrecognized` | `event.target_audience == ''` | Warning logged |
| Re-sync | Event exists, column F changed | `target_audience` updated via `update_or_create` defaults | N/A |

</frozen-after-approval>

## Code Map

- `events/models/event.py` — `Event` model; add `TargetAudience` choices + `target_audience` field here
- `events/migrations/` — new migration for the field addition
- `dashboard/services/filbo.py` — `sync_filbo_event`; read col F, translate via mapping dict, add to defaults
- `dashboard/tests/services/test_filbo_sync_event.py` — new test file covering I/O matrix scenarios

## Tasks & Acceptance

**Execution:**
- [x] `events/models/event.py` -- add `TargetAudience(models.TextChoices)` inner class with 7 universal choices (`early_childhood`, `children`, `young_adult`, `adults`, `families`, `professionals`, `all_audiences`) and `target_audience = models.CharField(blank=True, max_length=50, choices=TargetAudience)` field -- stores audience segmentation generically on Event
- [x] `events/migrations/0042_event_target_audience.py` -- generate via `makemigrations` -- persists the new field
- [x] `dashboard/services/filbo.py` -- in `sync_filbo_event`: read `_get_event_field('F')`, translate via a local `FILBO_AUDIENCE_MAP` dict to `Event.TargetAudience` values, log a warning for non-empty unrecognized values, add `target_audience` to `defaults`; update column-mapping docstring to include F -- syncs the field on every run
- [x] `dashboard/tests/services/test_filbo_sync_event.py` -- new file; unit-test all six I/O matrix scenarios using a minimal `event_data` row stub (no live spreadsheet) -- verifies translation and edge cases

**Acceptance Criteria:**
- Given a FILBo row with `age_under_6` in column F, when synced, then `event.target_audience == 'early_childhood'`.
- Given a FILBo row with `age_13_27` in column F, when synced, then `event.target_audience == 'young_adult'`.
- Given a FILBo row with `young_adult` in column F, when synced, then `event.target_audience == 'young_adult'`.
- Given a FILBo row with `book_professionals` in column F, when synced, then `event.target_audience == 'professionals'`.
- Given a FILBo row with an empty column F, when synced, then `event.target_audience == ''`.
- Given a FILBo row with an unrecognized column-F value, when synced, then `event.target_audience == ''` and a warning is logged.
- Given an existing event is re-synced with a changed column-F value, when synced, then `target_audience` is updated to the new translated value.
- Given a non-FILBo event created directly, when saved, then `target_audience` defaults to `''` with no errors.

## Design Notes

FILBo column F → `TargetAudience` translation map:

```python
FILBO_AUDIENCE_MAP = {
    'age_under_6':        Event.TargetAudience.EARLY_CHILDHOOD,
    'age_6_12':           Event.TargetAudience.CHILDREN,
    'age_13_27':          Event.TargetAudience.YOUNG_ADULT,
    'age_over_27':        Event.TargetAudience.ADULTS,
    'book_professionals': Event.TargetAudience.PROFESSIONALS,
    'young_adult':        Event.TargetAudience.YOUNG_ADULT,
}
```

## Verification

**Commands:**
- `docker exec desparchado-web-1 sh -c "cd app && pytest dashboard/tests/services/test_filbo_sync_event.py --no-cov -v"` -- expected: all tests pass
- `docker exec desparchado-web-1 sh -c "cd app && ruff check events/models/event.py dashboard/services/filbo.py dashboard/tests/services/test_filbo_sync_event.py"` -- expected: no errors

## Suggested Review Order

**Schema & choices**

- Universal `TargetAudience` inner class; 7 choices, `blank=True`, indexed at `max_length=50`
  [`event.py:58`](../../events/models/event.py#L58)

**FILBo translation layer**

- Module-level map translating FILBo column F values to universal choices; see comment on `young_adult`
  [`filbo.py:26`](../../dashboard/services/filbo.py#L26)

- Column F extracted then translated; unknown values warn and fall back to `''`
  [`filbo.py:278`](../../dashboard/services/filbo.py#L278)

- `target_audience` added to `defaults` dict — updated on every sync run
  [`filbo.py:360`](../../dashboard/services/filbo.py#L360)

**Admin**

- Field added to the Information fieldset alongside `event_date` and `category`
  [`admin.py:96`](../../events/admin.py#L96)

- Field added to `list_filter` for sidebar filtering
  [`admin.py:107`](../../events/admin.py#L107)

**Tests & migration**

- 7 tests covering all I/O matrix scenarios including re-sync and warning assertion
  [`test_filbo_sync_event.py:1`](../../dashboard/tests/services/test_filbo_sync_event.py#L1)

- Migration adding the field with `db_index=True`
  [`0042_event_target_audience.py:1`](../../events/migrations/0042_event_target_audience.py#L1)
