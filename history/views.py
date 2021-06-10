from django.views.generic import ListView
from django.views.generic import DetailView

from .models import HistoricalFigure
from .models import Group


class HistoricalFigureListView(ListView):
    model = HistoricalFigure


class HistoricalFigureDetailView(DetailView):
    model = HistoricalFigure

    def get_object(self, queryset=None):
        return HistoricalFigure.objects.get(token=self.kwargs.get('token'))


class GroupDetailView(DetailView):
    model = Group

    def get_object(self, queryset=None):
        return Group.objects.get(token=self.kwargs.get('token'))
