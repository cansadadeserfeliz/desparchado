---
title: 'Special Detail — Filter UX: Past Chips, Place Filter, Active Filter Summary'
type: 'feature'
created: '2026-04-14'
status: 'done'
baseline_commit: 'ef859076bab498f3aacfe4890c6b170ae082354e'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The special detail filter bar has no way to filter by place, past date chips are visually indistinguishable from future ones, and once filters are applied there is no at-a-glance summary of what is active.

**Approach:** (1) Add `chip--past` modifier to date chips for dates before today. (2) Add a place dropdown populated only from places present in the special's published events. (3) Build a unified filter state object in the view and render a "Buscando por:" section in the template using existing chip/button HTML patterns; FE developer handles styling in a separate ticket.

## Boundaries & Constraints

**Always:**
- Place filter param name is `lugar`; value is the place primary key (integer).
- Place choices come only from `self.object.events.published()` — not all places in the DB.
- `chip--past` class is added when `event_date.date() < today`; the chip remains fully interactive.
- All four filters (date, search, target audience, place) stack cumulatively and submit via the single existing form.
- `lugar` included in `pagination_query_params` when active.
- Active filter summary shows only the filters that are currently applied; renders nothing when no filters are active.
- The "Buscando por:" section is rendered server-side in the template; no new Vue components introduced.

**Ask First:**
- Nothing flagged.

**Never:**
- Changes outside `specials/views.py`, `specials/templates/specials/special_detail.html`, `specials/tests/test_views.py`.
- New SCSS files or modifications to `chip.scss` (FE ticket owns styling for `chip--past` and filter summary).
- JS-based auto-form-submission on filter change.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Place filter active | `?lugar=42` (valid place in special) | Events narrowed to place 42 | N/A |
| Invalid place ID | `?lugar=abc` or `?lugar=99999` | Filter silently ignored; all events shown | Parse error → `None`; ORM filter skipped |
| Date in the past | `event_date < today` on a chip | Label rendered with `chip--past` class | N/A |
| All four filters active | `?busqueda=taller&fecha=2026-04-20&publico=familia&lugar=42` | All filters stack; summary shows all four entries | N/A |
| No filters active | No params | "Buscando por:" section absent from rendered HTML | N/A |
| Multiple dates in summary | `?fecha=2026-04-20&fecha=2026-04-22` | Summary lists each date individually (not as a range) | N/A |

</frozen-after-approval>

## Code Map

- `specials/views.py` — `SpecialDetailView.get_context_data`: rename params to Spanish, add place filter logic, build unified `filters` dict
- `specials/templates/specials/special_detail.html` — chip--past class, lugar select, "Buscando por:" section using `filters` dict
- `specials/tests/test_views.py` — new tests using renamed params and `filters` context key

## Tasks & Acceptance

**Execution:**
- [x] `specials/views.py` — Rename `search_query_name = "busqueda"` (class attr). Use `audience_filter_name = "publico"` locally. Parse `lugar` → `int | None`. Query `place_choices` as `(id, name)` from `self.object.events.published().select_related("place").values_list("place_id", "place__name").distinct().order_by("place__name")`. Apply filters (search, fecha, publico, lugar) independently on `events_queryset`. Build `filters` dict: `{"selected_dates": list[date], "search": str, "audience": str, "audience_label": str, "place_id": int|None, "place_name": str, "has_any": bool}` — `audience_label` from `dict(Event.TargetAudience.choices)`, `place_name` from `place_choices` lookup (fallback `""`), `has_any = bool(selected_dates or has_search or audience or place_id is not None)`. Pass `filters`, `audience_filter_name`, `place_filter_name`, `date_filter_name`, `search_filter_name` to context. Remove separate `selected_dates`, `search_string`, `target_audience_filter_value`, `place_filter_value` context keys.
- [x] `specials/templates/specials/special_detail.html` — Update form: `name="{{ search_filter_name }}"` on input, value from `filters.search`; audience select uses `audience_filter_name` and `filters.audience`; place select uses `place_filter_name` and `filters.place_id`; chip checked uses `filters.selected_dates`. Chip past class: `{% if event_date < today %}chip--past{% endif %}`. "Buscando por:" block: `{% if filters.has_any %}` — list each active filter (fecha, busqueda, publico, lugar) as a chip with `href="{{ request.path }}#events"` for all clear links. Dates section lists each date individually: `{% for d in filters.selected_dates %}{{ d|date:'D, b j' }}{% endfor %}`.
- [x] `specials/tests/test_views.py` — Update all existing tests using `'q'` → `'busqueda'` and `'target_audience'` → `'publico'`. New tests: (1) `lugar` filters to matching place; (2) invalid `lugar` ignored; (3) `filters.place_name` populated when valid `lugar` passed; (4) `filters.has_any` is False with no params; (5) chip count for `chip--past` is exactly 1 when one past and one future event exist.

**Acceptance Criteria:**
- Given a published event at Place A and B, when `?lugar=<Place A id>` submitted, only Place A's event appears.
- Given no `lugar` param, both events listed and "Buscando por:" section is absent.
- Given an event date before today, its chip label has the `chip--past` CSS class.
- Given all four filters active, "Buscando por:" shows four chips each with a clear link to `request.path#events`.
- Given no filters active, the "Buscando por:" section is not present in the HTML.
- Given three non-contiguous dates selected, "Buscando por: Fecha" shows three individual dates, not a range.

## Spec Change Log

- **2026-04-14 — human renegotiation (bad_spec x4):**
  (1) Removed `_build_clear_url` helper — over-engineered; all clear links use `{{ request.path }}#events`. (2) Date summary changed from first–last range to listing individual dates — range was misleading for non-contiguous selections. (3) Filter param names made consistently Spanish: `q` → `busqueda`, `target_audience` → `publico`. (4) Replaced `active_filter_summary` list + separate `selected_dates`/`search_string`/`place_filter_value` context vars with a single `filters` dict serving both form-state restoration and "Buscando por:" display.
  KEEP: `chip--past` class approach, `place_choices` query from special's published events, `place_id` ORM filter, template structural layout, test factory patterns.

## Design Notes

**`filters` unified dict** — single context key replaces five separate ones; template reads `filters.search` for input value, `filters.selected_dates` for chip checked state, `filters.audience`/`filters.place_id` for select state, and `filters.has_any` to show/hide the "Buscando por:" section:

```python
filters = {
    "selected_dates": selected_dates,      # list[date] — chip checked state
    "search": search_query_value,          # str — input value
    "audience": audience_value,            # str — select state
    "audience_label": audience_label,      # str — display label
    "place_id": place_filter_value,        # int | None — select state
    "place_name": place_name,              # str — display label
    "has_any": bool(...),                  # bool — show/hide summary
}
```

**Individual date display** — template loops `filters.selected_dates` directly with `|date:'D, b j'` filter, comma-separated. No pre-formatting in the view.

## Verification

**Commands:**
- `docker exec desparchado-web-1 sh -c "cd app && pytest specials/tests/test_views.py -v"` -- expected: all tests pass
- `docker exec desparchado-web-1 sh -c "cd app && ruff check specials/views.py"` -- expected: no errors

**Manual checks (if no CLI):**
- Place dropdown appears in the filter bar; selecting a place and submitting narrows events.
- Past-date chips carry `chip--past` class (inspect element).
- "Buscando por:" section appears when at least one filter is active; clear links navigate to the unfiltered page.
- Selecting three non-contiguous dates shows three individual dates in the summary (not a range).

## Suggested Review Order

**Place filter (entry point — new filter param + ORM logic)**

- `lugar` parsed to `int | None`; silent `ValueError` → no filter; class attr `search_query_name = "busqueda"`.
  [`views.py:63`](../../specials/views.py#L63)

- `place_choices` built from this special's published events only, ordered by name.
  [`views.py:74`](../../specials/views.py#L74)

- Place and audience ORM filters both guarded; all four filters apply independently.
  [`views.py:95`](../../specials/views.py#L95)

- `lugar` appended to `param_pairs` so pagination links preserve the active filter.
  [`views.py:122`](../../specials/views.py#L122)

**Unified `filters` dict (view → template pipeline)**

- `filters` dict built: raw values for form-state restoration + labels for display.
  [`views.py:145`](../../specials/views.py#L145)

- `has_any` is the sole gate for the "Buscando por:" block; `place_filter_value is not None` ensures 0 would still count.
  [`views.py:160`](../../specials/views.py#L160)

- Template drives all form state from `filters.*`; no separate `selected_dates`/`search_string` vars.
  [`special_detail.html:66`](../../specials/templates/specials/special_detail.html#L66)

**Past-chip class and "Buscando por:" section (template)**

- `chip--past` added inline; chip remains a checkbox label — no interactivity change.
  [`special_detail.html:88`](../../specials/templates/specials/special_detail.html#L88)

- "Buscando por:" block: each filter chip renders its own `{{ d|date:'D, b j' }}` loop; all clear links go to `request.path#events`.
  [`special_detail.html:117`](../../specials/templates/specials/special_detail.html#L117)

**Tests**

- Renamed-param tests (`busqueda`, `publico`) validate the full filter stack.
  [`test_views.py:44`](../../specials/tests/test_views.py#L44)

- Place filter and invalid-ID tests; `filters.place_name` assertion.
  [`test_views.py:171`](../../specials/tests/test_views.py#L171)

- `has_any` false / chip count exactly 1 for past modifier.
  [`test_views.py:210`](../../specials/tests/test_views.py#L210)