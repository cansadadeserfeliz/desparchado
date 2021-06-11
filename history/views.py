from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from .models import HistoricalFigure, Event


class HistoricalFigureListView(ListView):
    model = HistoricalFigure


class EventsListView(ListView):
    model = Event


class EventDetailView(DetailView):
    model = Event

    def get_object(self, queryset=None):
        return Event.objects.get(token=self.kwargs.get("token"))
