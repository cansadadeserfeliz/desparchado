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

    The view supports:
    - Filtering events by a selected.
    - Searching events by keyword.
    - Pagination of event results.

    Behavior:
    - If a search query (`q`) is provided and its length >= `search_query_min_length`,
      events are filtered using the `search_events` service.
    - Otherwise, events are filtered by date (`fecha`). If no date is given, it defaults
      to today’s date (if available) or the earliest available event date.
    """
    model = Special
    search_query_name = "q"
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
        selected_date_param = "fecha"
        raw_dates = self.request.GET.getlist(selected_date_param)
        selected_dates: list[date] = [d for raw in raw_dates if (d := parse_date(raw))]
        search_query_value = self.request.GET.get(self.search_query_name, "")

        target_audience_filter_name = 'target_audience'
        target_audience_filter_value = self.request.GET.get(
            target_audience_filter_name, '',
        )
        if target_audience_filter_value not in Event.TargetAudience:
            target_audience_filter_value = ''

        # Apply search or date filter
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
        elif selected_dates:
            events_queryset = events_queryset.filter(
                event_date__date__in=selected_dates,
            )

        # Apply target_audience filter independently (stacks with search or date)
        if target_audience_filter_value:
            events_queryset = events_queryset.filter(
                target_audience=target_audience_filter_value,
            )

        # Optimize query performance
        events_queryset = (
            events_queryset.select_related("place")
            .prefetch_related("speakers")
            .order_by("event_date")
        )

        # Pagination
        try:
            page_number = int(self.request.GET.get('page', 1))
        except ValueError:
            page_number = 1

        paginator = Paginator(events_queryset, 30)
        page = paginator.get_page(page_number)

        param_pairs: list[tuple[str, str]] = [
            (selected_date_param, str(d)) for d in selected_dates
        ]
        if has_search:
            param_pairs.append((self.search_query_name, search_query_value))
        if target_audience_filter_value:
            param_pairs.append(
                (target_audience_filter_name, target_audience_filter_value),
            )
        pagination_query_params = f"&{urlencode(param_pairs)}" if param_pairs else ""

        present_values = set(
            self.object.events.published()
            .exclude(target_audience='')
            .values_list('target_audience', flat=True)
            .distinct(),
        )
        target_audience_choices = [
            (value, label)
            for value, label in Event.TargetAudience.choices
            if value in present_values
        ]

        # Context setup
        context.update(
            {
                "events": page.object_list,
                "paginator": paginator,
                "page_obj": page,
                "is_paginated": page.has_other_pages(),
                "selected_date_param": selected_date_param,
                "event_dates": event_dates,
                "selected_dates": selected_dates,
                "search_string": search_query_value,
                "today": today,
                "pagination_query_params": pagination_query_params,
                "target_audience_filter_name": target_audience_filter_name,
                "target_audience_filter_value": target_audience_filter_value,
                "target_audience_choices": target_audience_choices,
            },
        )
        return context
