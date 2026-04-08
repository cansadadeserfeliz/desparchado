# Deferred Work

## Multi-value target_audience cells in FILBo sync

**Source:** Review of `feature/filbo-target-audience` (spec-event-target-audience)
**Finding:** Column F in the FILBo spreadsheet could theoretically contain comma- or semicolon-separated values (e.g. `age_6_12,age_13_27`). The current implementation treats the entire cell as a single lookup key, which would log a warning and store `''`. The `target_audience` field is a single `CharField`, so storing multiple audiences would require a structural change (M2M or ArrayField).
**Action if needed:** Confirm with FILBo data whether multi-value cells actually occur; if so, decide on storage strategy before implementing.