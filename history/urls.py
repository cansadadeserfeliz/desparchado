from django.urls import path

from .views import (
    EventDetailView,
    EventsListView,
    GroupDetailView,
    HistoricalFigureDetailView,
    HistoricalFigureListView,
    HistoryIndexTemplateView,
    PostDetailView,
    api_post_list,
)

app_name = 'history'
urlpatterns = [
    path('', HistoryIndexTemplateView.as_view(), name='index'),
    path(
        'personajes-historicos/',
        HistoricalFigureListView.as_view(),
        name='historical_figure_list',
    ),
    path(
        'personajes-historicos/<uuid:token>/',
        HistoricalFigureDetailView.as_view(),
        name='historical_figure_detail',
    ),
    path('posts/<uuid:token>/', PostDetailView.as_view(), name='post_detail'),
    path('grupos/<uuid:token>/', GroupDetailView.as_view(), name='group_detail'),
    path('eventos/', EventsListView.as_view(), name='event_list'),
    path('eventos/<uuid:token>/', EventDetailView.as_view(), name='event_detail'),
    path('api/posts/', api_post_list, name='api_post_list'),
]
