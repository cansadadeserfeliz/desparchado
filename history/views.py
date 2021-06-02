from django.views.generic import ListView

from .models import HistoricalFigure


class HistoricalFigureListView(ListView):
    model = HistoricalFigure
