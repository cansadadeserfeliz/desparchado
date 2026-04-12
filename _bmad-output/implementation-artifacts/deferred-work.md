# Deferred Work

## Special detail: pagination drops search query when date + search are combined

**Source:** Review of `spec-special-detail-unified-filters`
**Finding:** `pagination_query_params` is built from `selected_dates` and `target_audience_filter_value` only. When both a text search (`q`) and date chips are active simultaneously (currently mutually exclusive in the view, but may change), paginating would drop the search term.
**Action if needed:** Include `q` in `pagination_query_params` if search and date filtering are ever made combinable.

## Special detail: arbitrary `fecha` values pollute pagination params

**Source:** Review of `spec-special-detail-unified-filters`
**Finding:** A user-supplied `fecha` value that is a valid date but not in `event_dates` is parsed and included in `pagination_query_params`. It produces no visible chip but persists across pagination links. Low severity since it doesn't affect displayed results.
**Action if needed:** Filter `selected_dates` against `event_dates` before building `param_pairs`.

## Static error pages: 500.html Vite asset fragility during server errors

**Source:** Review of `spec-static-pages-new-design`
**Finding:** `500.html` uses `{% load django_vite %}` and `{% vite_asset %}`, as does `base.html` which it extends. If the Vite manifest is unavailable when a 500 error occurs (e.g. corrupt build artifact), template rendering will itself fail, causing Django to return a bare HTML-less 500 response. This is a pre-existing risk introduced by the existing `base.html` Vite usage and was not worsened by this story, but it is worth addressing.
**Action if needed:** Consider making `500.html` self-contained (no template inheritance, inline critical CSS) to guarantee it always renders, even if the build pipeline is broken.

## Multi-value target_audience cells in FILBo sync

**Source:** Review of `feature/filbo-target-audience` (spec-event-target-audience)
**Finding:** Column F in the FILBo spreadsheet could theoretically contain comma- or semicolon-separated values (e.g. `age_6_12,age_13_27`). The current implementation treats the entire cell as a single lookup key, which would log a warning and store `''`. The `target_audience` field is a single `CharField`, so storing multiple audiences would require a structural change (M2M or ArrayField).
**Action if needed:** Confirm with FILBo data whether multi-value cells actually occur; if so, decide on storage strategy before implementing.