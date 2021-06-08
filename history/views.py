from django.views.generic import ListView
from django.shortcuts import render

from .models import HistoricalFigure, Event


class HistoricalFigureListView(ListView):
    model = HistoricalFigure


class EventsListView(ListView):
    model = Event


def eventdetail(request, token):
    event = Event.objects.get(token=token)
    return render(request, "history/event_detail.html", {"event": event})
