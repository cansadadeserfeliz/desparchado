from django.views.generic import ListView, DetailView
from django.utils import timezone

from .models import Event


class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            is_published=True,
            event_date__gte=timezone.now(),
        )
        return queryset.select_related('place')


class EventDetailView(DetailView):
    model = Event


