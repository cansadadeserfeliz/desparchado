from django.db.models.functions import TruncDate
from django.views.generic import DetailView
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date

from .models import Special


class SpecialDetailView(DetailView):
    model = Special

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_events = self.object.events.published().all()

        event_dates = related_events.annotate(
            event_date_only=TruncDate('event_date')
        ).values_list('event_date_only', flat=True).order_by('event_date_only').distinct()

        today = now().date()

        selected_date_param = 'fecha'
        selected_date = parse_date(self.request.GET.get(selected_date_param, ''))
        if not selected_date:
            if today in event_dates:
                selected_date = today
            else:
                selected_date = event_dates[0]

        selected_date_events = related_events.filter(event_date__date=selected_date).order_by('event_date')

        # Pagination
        page_number = self.request.GET.get('page', 1)
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1

        paginator = Paginator(selected_date_events, 30)
        page = paginator.get_page(page_number)
        context['events'] = page.object_list
        context['paginator'] = paginator
        context['page_obj'] = page
        context['is_paginated'] = page.has_other_pages()

        context['selected_date_param'] = selected_date_param
        context['event_dates'] = event_dates
        context['selected_date'] = selected_date
        context['today'] = today
        return context
