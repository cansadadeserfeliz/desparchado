from django.views.generic import ListView

from .models import HistoricalFigure, Event


class HistoricalFigureListView(ListView):
    model = HistoricalFigure


class EventsListView(ListView):
    model = Event
