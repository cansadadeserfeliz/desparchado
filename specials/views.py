from datetime import date
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.views.generic import DetailView

from events.models import Event
from events.services import search_events

from .models import Special


class SpecialDetailView(DetailView):
    """
    Displays details of a `Special` instance and its related published events.

    All filters stack cumulatively:
    - `busqueda`: full-text search via `search_events` when >= min chars.
    - `fecha`: one or more dates; events are filtered to the union of those dates.
    - `publico`: narrows results to the given audience value.
    - `lugar`: narrows results to events at the given place (primary key).

    When no filters are active, all published events for the special are returned.
    """
    model = Special
    search_query_name = "busqueda"
    search_query_min_length = 3

    def get_queryset(self):
        """Return only published specials."""
        queryset = super().get_queryset()
        return queryset.filter(is_published=True)

    def get_context_data(self, **kwargs):
        """Add filtered, searched and paginated events to the context."""
        context = super().get_context_data(**kwargs)
        events_queryset = self.object.events.published().all()

        # Collect distinct event dates (for date selector UI)
        event_dates = (
            events_queryset.annotate(event_date_only=TruncDate('event_date'))
            .values_list('event_date_only', flat=True)
            .order_by('event_date_only')
            .distinct()
        )

        today = now().date()

        # --- Parse filter params ---
        date_filter_name = "fecha"
        raw_dates = self.request.GET.getlist(date_filter_name)
        selected_dates: list[date] = [d for raw in raw_dates if (d := parse_date(raw))]

        search_filter_name = self.search_query_name
        search_query_value = self.request.GET.get(search_filter_name, "")

        audience_filter_name = "publico"
        audience_value = self.request.GET.get(audience_filter_name, "")
        if audience_value not in Event.TargetAudience:
            audience_value = ""

        place_filter_name = "lugar"
        raw_place = self.request.GET.get(place_filter_name, "")
        try:
            place_filter_value: int | None = int(raw_place)
        except (ValueError, TypeError):
            place_filter_value = None

        # --- Build place choices from this special's published events only ---
        place_choices: list[tuple[int, str]] = list(
            self.object.events.published()
            .select_related("place")
            .values_list("place_id", "place__name")
            .distinct()
            .order_by("place__name"),
        )

        # --- Apply filters independently (all four can stack) ---
        has_search = (
            search_query_value
            and len(search_query_value) >= self.search_query_min_length
        )
        if has_search:
            events_queryset = search_events(
                queryset=events_queryset,
                search_str=search_query_value,
                search_str_min_length=self.search_query_min_length,
            )
        if selected_dates:
            events_queryset = events_queryset.filter(
                event_date__date__in=selected_dates,
            )
        if audience_value:
            events_queryset = events_queryset.filter(target_audience=audience_value)
        if place_filter_value is not None:
            events_queryset = events_queryset.filter(place_id=place_filter_value)

        # Optimize query performance
        events_queryset = (
            events_queryset.select_related("place")
            .prefetch_related("speakers")
            .order_by("event_date")
        )

        # --- Pagination ---
        try:
            page_number = int(self.request.GET.get("page", 1))
        except ValueError:
            page_number = 1

        paginator = Paginator(events_queryset, 30)
        page = paginator.get_page(page_number)

        param_pairs: list[tuple[str, str]] = [
            (date_filter_name, str(d)) for d in selected_dates
        ]
        if has_search:
            param_pairs.append((search_filter_name, search_query_value))
        if audience_value:
            param_pairs.append((audience_filter_name, audience_value))
        if place_filter_value is not None:
            param_pairs.append((place_filter_name, str(place_filter_value)))
        pagination_query_params = f"&{urlencode(param_pairs)}" if param_pairs else ""

        # --- Audience choices (only values present in this special's events) ---
        present_audience_values = set(
            self.object.events.published()
            .exclude(target_audience="")
            .values_list("target_audience", flat=True)
            .distinct(),
        )
        audience_choices = [
            (value, label)
            for value, label in Event.TargetAudience.choices
            if value in present_audience_values
        ]

        # --- Unified filters dict (form state + display) ---
        audience_label = (
            dict(Event.TargetAudience.choices).get(audience_value, "")
            if audience_value
            else ""
        )
        place_name = (
            next((name for pid, name in place_choices if pid == place_filter_value), "")
            if place_filter_value is not None
            else ""
        )

        # All currently active params — used to build per-filter clear URLs
        all_params: list[tuple[str, str]] = (
            [(date_filter_name, str(d)) for d in selected_dates]
            + ([(search_filter_name, search_query_value)] if has_search else [])
            + ([(audience_filter_name, audience_value)] if audience_value else [])
            + (
                [(place_filter_name, str(place_filter_value))]
                if place_filter_value is not None
                else []
            )
        )
        base_path = self.request.path

        def _clear_url(exclude_key: str) -> str:
            remaining = [(k, v) for k, v in all_params if k != exclude_key]
            qs = urlencode(remaining)
            return f"{base_path}?{qs}#events" if qs else f"{base_path}#events"

        filters = {
            "selected_dates": selected_dates,
            "search": search_query_value,
            "audience": audience_value,
            "audience_label": audience_label,
            "place_id": place_filter_value,
            "place_name": place_name,
            "has_any": bool(
                selected_dates
                or has_search
                or audience_value
                or place_filter_value is not None,
            ),
            "date_clear_url": _clear_url(date_filter_name),
            "search_clear_url": _clear_url(search_filter_name),
            "audience_clear_url": _clear_url(audience_filter_name),
            "place_clear_url": _clear_url(place_filter_name),
        }

        # --- Context setup ---
        context.update(
            {
                "events": page.object_list,
                "paginator": paginator,
                "page_obj": page,
                "is_paginated": page.has_other_pages(),
                "date_filter_name": date_filter_name,
                "search_filter_name": search_filter_name,
                "audience_filter_name": audience_filter_name,
                "place_filter_name": place_filter_name,
                "event_dates": event_dates,
                "today": today,
                "pagination_query_params": pagination_query_params,
                "audience_choices": audience_choices,
                "place_choices": place_choices,
                "filters": filters,
            },
        )
        return context
