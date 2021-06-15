from django.urls import path

from django.views.generic import TemplateView
from .views import HistoricalFigureListView
from .views import HistoricalFigureDetailView
from .views import PostDetailView
from .views import GroupDetailView
from .views import EventsListView
from .views import EventDetailView


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
        'personajes-historicos/<uuid:token>/',
        HistoricalFigureDetailView.as_view(),
        name='historical_figure_detail'
    ),
    path(
        'posts/<uuid:token>/',
        PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'grupos/<uuid:token>/',
        GroupDetailView.as_view(),
        name='group_detail'
    ),
    path(
        'eventos/',
        EventsListView.as_view(),
        name='event_list'
    ),
    path(
        'eventos/<uuid:token>/',
        EventDetailView.as_view(),
        name='event_detail'
    ),
]
