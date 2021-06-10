from django.views.generic import ListView
from django.views.generic import DetailView

from .models import HistoricalFigure


class HistoricalFigureListView(ListView):
    model = HistoricalFigure


class HistoricalFigureDetailView(DetailView):
    model = HistoricalFigure

    def get_object(self, queryset=None):
        return HistoricalFigure.objects.get(token=self.kwargs.get('token'))
