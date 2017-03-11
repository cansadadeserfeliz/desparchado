from django.views.generic import DetailView

from .models import Event


class EventDetailView(DetailView):
    model = Event
