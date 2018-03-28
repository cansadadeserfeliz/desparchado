from django.views.generic import ListView, DetailView
from django.utils import timezone

from .models import Event, Organizer, Speaker


class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    paginate_by = 9

    def get_queryset(self):
        queryset = Event.objects.published().future()
        return queryset.select_related('place')


class PastEventListView(ListView):
    model = Event
    context_object_name = 'events'
    template_name = 'events/past_event_list.html'
    paginate_by = 9

    def get_queryset(self):
        queryset = Event.objects.published().past().order_by('-event_date')
        return queryset.select_related('place')


class EventDetailView(DetailView):
    model = Event

    def get_queryset(self):
        return Event.objects.published().all()


class OrganizerListView(ListView):
    model = Organizer
    context_object_name = 'organizers'
    paginate_by = 9


class OrganizerDetailView(DetailView):
    model = Organizer


class SpeakerDetailView(DetailView):
    model = Speaker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = \
            self.get_object().events.published().future().all()[:9]
        context['past_events'] = \
            self.get_object().events.published().past().order_by('-event_date').all()[:9]
        return context


class SpeakerListView(ListView):
    model = Speaker
    context_object_name = 'speakers'
    paginate_by = 9
