---
title: 'target_audience filter on future events list and special page'
type: 'feature'
created: '2026-04-07'
status: 'done'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The new `target_audience` field on `Event` is not exposed to users, so the ~8 000 existing events without a value would make a blanket filter meaningless and confusing — especially for past events.

**Approach:** Add a `target_audience` dropdown filter to the future events list page and the special detail page only. The filter renders dynamically: options are derived from the full unpaginated queryset for that page so choices on later pages are always visible; if no event has a `target_audience` value, the entire filter is hidden.

## Boundaries & Constraints

**Always:**
- Filter is added to **future events list** (`EventListView`) and **special detail page** (`SpecialDetailView`) only — no other pages.
- Available choices are derived from the full unpaginated base queryset for each page (all future published events for the event list; all of the special's published events for the special page) — not from the current page slice — so an option is never hidden just because matching events fall on a later page.
- Empty `target_audience` values (`''`) are always excluded from the available choices list.
- If zero options remain after exclusion, the `<select>` is hidden entirely via a template conditional.
- The filter is a native HTML `<select>` element inside the existing `select-group` row, visually matching the city and category filters.
- Query param name: `target_audience` (e.g. `?target_audience=young_adult`).
- Invalid (unrecognized) param values are silently ignored (treat as no filter applied).
- On the event list, `target_audience` is applied on top of city and category filters — all three combine via `.filter()` chaining on the same queryset.
- On the special page, `target_audience` is applied as an independent `.filter()` after the search/date if/else block — it stacks with whichever of those is active.
- `target_audience` must be added to the `params` dict that builds `pagination_query_params` in both views so it is included in every pagination link and survives page navigation alongside other active filters.
- No caching — choices are computed on every request.

**Ask First:** None anticipated.

**Never:**
- Do not add this filter to the past events list.
- Do not add this filter to any detail pages (event, speaker, organizer, place).
- Do not use a Vue component for the filter — keep it as a native `<select>`.
- Do not show all 7 `TargetAudience` choices unconditionally; always derive from actual event data.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Active filter | `?target_audience=young_adult`, events exist with that value | Only matching events returned; option shown as selected | N/A |
| No events with target_audience | All future events have `target_audience=''` | Filter `<select>` not rendered | N/A |
| Partial coverage | Some choices present, some absent | Only present choices shown in dropdown | N/A |
| Invalid param value | `?target_audience=nonsense` | Ignored; all events returned; no filter applied | Silent ignore |
| Event list: audience + category | `?target_audience=children&category=literature` | Both filters applied; only events matching both returned | N/A |
| Event list: audience + city + category | `?target_audience=children&city=bogota&category=science` | All three filters combined | N/A |
| Filter + pagination | `?target_audience=children&page=2` | `target_audience` present in every pagination link; filter persists on page navigation | N/A |
| Filter + other active filters + pagination | `?target_audience=adults&city=bogota&page=3` | Both `target_audience` and `city` preserved in pagination links | N/A |
| Special page: filter + date | `?target_audience=adults&fecha=2026-04-28` | Date filter and audience filter both applied to queryset | N/A |
| Special page: filter + search | `?target_audience=adults&q=poesia` | Search filter and audience filter both applied to queryset | N/A |
| Special page: filter + date + pagination | `?target_audience=adults&fecha=2026-04-28&page=2` | Both `target_audience` and `fecha` in pagination links | N/A |

</frozen-after-approval>

## Code Map

- `events/views/event_list.py` — `EventListBaseView` (dispatch, get_queryset, get_context_data) and `EventListView` (available choices computation from full unpaginated queryset)
- `events/templates/events/event_list.html` — add `<select>` inside existing `select-group`, conditional on choices being non-empty
- `events/templates/events/_event_list_pagination.html` — **no changes needed**; shared partial already consumes `pagination_query_params` via `{% include ... with %}`; both `event_list.html` and `special_detail.html` pass this variable to it, so adding `target_audience` to `pagination_query_params` in the view is sufficient
- `specials/views.py` — `SpecialDetailView.get_context_data`: read param, validate, filter queryset, compute choices, update pagination params
- `specials/templates/specials/special_detail.html` — add `<select>` inside search form, conditional
- `events/tests/views/test_event_list.py` — new tests for filtering behavior
- `specials/tests/test_views.py` — new tests for filtering behavior on special page

## Tasks & Acceptance

**Execution:**
- [ ] `events/views/event_list.py` -- add `target_audience_filter_name`/`target_audience_filter_value` attrs to `EventListBaseView`; validate and apply filter in `dispatch` and `get_queryset`; pass filter name/value and update `pagination_query_params` in `get_context_data`; in `EventListView.get_context_data` compute `target_audience_choices` from the full unpaginated future published queryset (no caching) -- backend support for the filter
- [ ] `events/templates/events/event_list.html` -- add `<select name="target_audience">` inside the `select-group` div after the city filter, guarded by `{% if target_audience_choices %}` -- renders filter only when relevant options exist
- [ ] `specials/views.py` -- read and validate `?target_audience=` param; apply as independent `.filter()` after the search/date if/else block so it stacks with both; compute `target_audience_choices` from the special's full published event set; add filter name/value and choices to context; when `target_audience` is active, add it to the `params` dict that builds `pagination_query_params` alongside `selected_date_param` -- backend support on the special page
- [ ] `specials/templates/specials/special_detail.html` -- add `<select name="target_audience">` inside the search form, guarded by `{% if target_audience_choices %}` -- renders filter only when relevant options exist
- [ ] `events/tests/views/test_event_list.py` -- add tests: filter returns only matching events; invalid value ignored; events with empty target_audience excluded from choices -- verifies event list filter behavior
- [ ] `specials/tests/test_views.py` -- add tests: filter returns only matching events on special page; stacks with date filter -- verifies special page filter behavior

**Acceptance Criteria:**
- Given future events exist with `target_audience='young_adult'`, when visiting `/events/`, then a `<select>` for target_audience is present with a `young_adult` option.
- Given all future events have `target_audience=''`, when visiting `/events/`, then no target_audience `<select>` is rendered.
- Given `?target_audience=young_adult` in the URL, when the event list loads, then only events with `target_audience='young_adult'` are returned.
- Given `?target_audience=nonsense` in the URL, when the event list loads, then the filter is ignored and all future events are returned.
- Given `?target_audience=adults&page=2`, when navigating to page 2, then `target_audience=adults` is preserved in the pagination links.
- Given a special page with events having `target_audience='professionals'`, when filtering by `?target_audience=professionals&fecha=2026-04-28`, then only events matching both date and audience are returned.
- Given a special page where no events have a `target_audience` value, when viewing the page, then no target_audience `<select>` is rendered.

## Verification

**Commands:**
- `docker exec desparchado-web-1 sh -c "cd app && pytest events/tests/views/test_event_list.py specials/tests/test_views.py --no-cov -v"` -- expected: all tests pass
- `docker exec desparchado-web-1 sh -c "cd app && ruff check events/views/event_list.py specials/views.py"` -- expected: no errors