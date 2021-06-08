from django.urls import path

from django.views.generic import TemplateView
from .views import HistoricalFigureListView, EventsListView


app_name = 'history'
urlpatterns = [
    path(
        '',
        TemplateView.as_view(template_name='history/index.html'),
        name='index'
    ),
    path(
        'personajes-historicos/',
        HistoricalFigureListView.as_view(),
        name='historical_figure_list'
    ),
    path(
        'eventos/',
        EventsListView.as_view(),
        name='event_list',
    ),
]
