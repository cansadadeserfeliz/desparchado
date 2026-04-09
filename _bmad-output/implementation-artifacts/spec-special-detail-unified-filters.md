---
title: 'Special Detail — Unified Filters & Multi-Date Selection'
type: 'feature'
created: '2026-04-08'
status: 'done'
baseline_commit: '83a365fb15da62218127d923f78162704ff68ad0'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** On the special detail page, the date filter navigates immediately on chip click while search and audience filter require an explicit form submit, creating inconsistent UX. Users cannot select multiple dates or deselect a chosen date.

**Approach:** Move the date chips inside the search form as styled checkboxes. The form's "Buscar" button becomes the single submission point for all filters. Extend the backend to accept multiple `fecha` values and return the union of events for all selected dates. Add Umami tracking attributes to the submit button and date chips.

## Boundaries & Constraints

**Always:**
- All three filters (date checkboxes, search query, target audience) submit via the same form submit button.
- Multiple selected dates are passed as repeated `fecha` query params; backend applies `event_date__date__in`.
- `data-umami-event="special-date-filter"` on each date chip label; `data-umami-event="special-event-search"` on the submit button.
- When no `fecha` params are present, no date filter is applied and all published events are shown with no chip checked.
- Event cards on this page get `data-vue-prop-umami-event="special-event-card"`.

**Ask First:**
- If `:has()` CSS selector support is not acceptable for the project's browser targets, switch to a small JS toggle approach instead.

**Never:**
- JS-based auto-form-submission on filter change.
- Changes outside `specials/views.py`, `special_detail.html`, or `chip.scss`.
- Removing the "Limpiar búsqueda" clear button.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| No params | No `fecha`, `q`, `target_audience` | All published events shown; no chip checked | N/A |
| Single date selected | `?fecha=2026-04-08` | Events for that date only; chip shows checked state | N/A |
| Multiple dates selected | `?fecha=2026-04-08&fecha=2026-04-09` | Union of events from both dates; both chips show checked | N/A |
| All chips unchecked, no other filter | No `fecha`, no `q`, no `target_audience` | All published events shown; no chip checked | N/A |
| All chips unchecked + audience filter | No `fecha`, `target_audience=familia` | No date filter; audience filter applied to all events | N/A |
| Search + date combined | `?q=taller&fecha=2026-04-08` | Full-text search applied first, then date filter narrows results | Query < 3 chars: ignored |
| Search only | `?q=taller` | Full-text search across all dates; no date filter applied | Query < 3 chars: ignored |
| Invalid `fecha` value | `?fecha=not-a-date` | Invalid value silently dropped; remaining valid dates used | N/A |

</frozen-after-approval>

## Code Map

- `specials/views.py` — `SpecialDetailView.get_context_data`: date parsing, filtering, context
- `specials/templates/specials/special_detail.html` — date chips, form structure, Umami attributes, event cards
- `desparchado/frontend/styles/forms/inputs/chip.scss` — chip selected state via `:has()`, hidden checkbox style
- `specials/tests/test_views.py` — view tests for multi-date filtering

## Tasks & Acceptance

**Execution:**
- [x] `specials/views.py` -- Replace `GET.get(selected_date_param)` with `GET.getlist(selected_date_param)`; parse each raw value through `parse_date`, discard invalids; apply `event_date__date__in=selected_dates` when list is non-empty; update auto-select logic to populate `selected_dates = [date]`; rebuild pagination params as `urlencode([(selected_date_param, d) for d in selected_dates] + [(target_audience_filter_name, target_audience_filter_value)] if ...)` using a list of tuples; pass `selected_dates` (list) to context instead of `selected_date`
- [x] `specials/templates/specials/special_detail.html` -- Move `.chip-group` div inside `#event_search_form` (before or after the text/audience inputs); replace each `<a class="chip ...">` with `<label class="chip" data-umami-event="special-date-filter">` wrapping `<input class="chip__checkbox" type="checkbox" name="fecha" value="{{ event_date|date:'Y-m-d' }}" {% if event_date in selected_dates %}checked{% endif %}>` and the existing date text; update submit button div to add `data-vue-prop-umami-event="special-event-search"`; add `data-vue-prop-umami-event="special-event-card"` to each `event-card-full-width` div
- [x] `desparchado/frontend/styles/forms/inputs/chip.scss` -- Add `.chip__checkbox { position: absolute; opacity: 0; width: 0; height: 0; }` and `.chip:has(input[type="checkbox"]:checked) { background-color: $color-layout-foreground; color: $color-layout-background; }` with matching hover/focus overrides so the `:has` rule wins over the default hover style when checked
- [x] `specials/tests/test_views.py` -- Add tests covering: single `fecha` param returns only that date's events; two `fecha` params return the union; invalid `fecha` is silently ignored; no `fecha` shows all events with no chip checked

**Acceptance Criteria:**
- Given the page loads with no params, when rendered, no chip is checked and all published events are listed.
- Given two date chips are checked and the form is submitted, when the page reloads, events from both dates appear in the list together.
- Given a checked chip is unchecked and "Buscar" is clicked, when the page reloads, events for only the remaining checked dates are shown.
- Given all chips are unchecked and audience filter is active, when "Buscar" is clicked, no date filter is applied (all audience-matched events shown).
- Given a search term and a date chip are both active, when the form is submitted, only events matching the search term on that date are shown.
- Given `ANALYTICS_ENABLED=True`, when the submit button is clicked, Umami fires `special-event-search`.
- Given `ANALYTICS_ENABLED=True`, when a date chip label is clicked, Umami fires `special-date-filter`.
- Given an event card is rendered, when clicked, Umami fires `special-event-card`.

## Spec Change Log

- **2026-04-08 — bug fix:** Search and date filters were mutually exclusive (`elif`). Fixed to stack independently (`if`/`if`). Updated I/O matrix (replaced "Search overrides date" with combined and search-only rows) and added AC for combined case. KEEP: all other filter behavior.
- **2026-04-08 — human renegotiation:** Removed auto-select behavior. Original spec auto-selected today/earliest date when no `fecha` param was present. User explicitly requested no default date on page load. Updated: Always boundary, I/O matrix rows "No params" and "All chips unchecked", task description, and AC. KEEP: all other behavior (multi-date union, invalid fecha dropped, chip-as-checkbox pattern, Umami tracking).

## Design Notes

**Checkbox-as-chip pattern** — the hidden checkbox is inside the label so the label click toggles the checkbox. CSS `:has(input[type="checkbox"]:checked)` applies the selected visual state without JS:

```html
<label class="chip" data-umami-event="special-date-filter">
  <input class="chip__checkbox" type="checkbox" name="fecha" value="2026-04-08" checked>
  mar., abr. 8
</label>
```

```scss
.chip:has(input[type="checkbox"]:checked) {
  background-color: $color-layout-foreground;
  color: $color-layout-background;
  &:hover, &:focus { background-color: $color-layout-foreground; color: $color-layout-background; }
}
```

**Umami on submit button** — `data-umami-event` goes on the outer `div[data-vue-component="button"]`, not as a Vue prop, because Umami reads DOM attributes directly:

```html
<div class="event-details__filter-action-item"
     data-vue-component="button"
     data-umami-event="special-event-search"
     ...>
</div>
```

## Verification

**Commands:**
- `docker exec -it desparchado-web-1 sh -c "cd app && pytest specials/tests/test_views.py -v"` -- expected: all tests pass
- `docker exec -it desparchado-web-1 sh -c "cd app && ruff check specials/views.py"` -- expected: no errors

**Manual checks (if no CLI):**
- On the special detail page: verify date chips are now inside the form; clicking chips toggles their checked appearance without page reload; "Buscar" reloads with the selected dates applied.
- With `ANALYTICS_ENABLED=True` and browser devtools open on Network: clicking "Buscar" fires a request to Umami with event `special-event-search`; clicking a date chip fires `special-date-filter`.

## Suggested Review Order

**Multi-date filtering (backend)**

- Entry point: `getlist` replaces `get`, walrus-parsed into `list[date]`
  [`views.py:54`](../../specials/views.py#L54)

- `__in` filter replaces single-date equality; auto-select writes into the list
  [`views.py:76`](../../specials/views.py#L76)

- Pagination params rebuilt as list of tuples for multi-value `urlencode`
  [`views.py:112`](../../specials/views.py#L112)

**Checkbox-as-chip (template)**

- Chip group moved inside form; `<a>` → `<label>` with hidden checkbox
  [`special_detail.html:94`](../../specials/templates/specials/special_detail.html#L94)

- Umami attribute on submit button (goes on the outer div, not as a Vue prop)
  [`special_detail.html:84`](../../specials/templates/specials/special_detail.html#L84)

- Umami attribute on event cards
  [`special_detail.html:128`](../../specials/templates/specials/special_detail.html#L128)

**CSS — checkbox selected state**

- `:has(input:checked)` drives selected state without JS; hover override locks color when checked
  [`chip.scss:33`](../../desparchado/frontend/styles/forms/inputs/chip.scss#L33)

- `.chip__checkbox` visually hidden with 1px size to preserve keyboard tab order
  [`chip.scss:47`](../../desparchado/frontend/styles/forms/inputs/chip.scss#L47)

**Tests**

- New test: two dates → union of events
  [`test_views.py:113`](../../specials/tests/test_views.py#L113)

- New test: invalid fecha silently dropped; valid one still applied
  [`test_views.py:147`](../../specials/tests/test_views.py#L147)

- New test: no fecha → shows all events with no chip checked
  [`test_views.py:172`](../../specials/tests/test_views.py#L172)