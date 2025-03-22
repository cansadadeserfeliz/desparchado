from django.db.models.functions import TruncDate
from django.views.generic import DetailView
from django.utils.timezone import now, localtime
from django.utils.dateparse import parse_date

from .models import Special
from events.models import Speaker


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

        date_param = 'fecha'
        selected_date = parse_date(self.request.GET.get(date_param, ''))
        if not selected_date:
            if today in event_dates:
                selected_date = today
            else:
                selected_date = event_dates[0]

        selected_date_events = related_events.filter(event_date__date=selected_date).order_by('event_date')

        speaker_ids = related_events.values_list('speakers__id', flat=True)
        context['speakers'] = Speaker.objects.filter(
            id__in=speaker_ids,
        ).exclude(image='').all()

        context['date_param'] = date_param
        context['event_dates'] = event_dates
        context['selected_date'] = selected_date
        context['events'] = selected_date_events
        return context
