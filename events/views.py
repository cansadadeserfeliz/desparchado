from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.http import Http404

from .models import Event, Organizer


class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    paginate_by = 9

    def get_queryset(self):
        queryset = Event.published.filter(
            event_date__gte=timezone.now(),
        )
        return queryset.select_related('place')


class EventDetailView(DetailView):
    model = Event

    def get_queryset(self):
        return Event.published.all()


class OrganizerListView(ListView):
    model = Organizer
    context_object_name = 'organizers'
    paginate_by = 9


class OrganizerDetailView(DetailView):
    model = Organizer
