from django.urls import path

from .views import UserAddedEventsListView, UserDetailView

app_name = 'users'
urlpatterns = [
    path(
        'added-events/',
        UserAddedEventsListView.as_view(),
        name='user_added_events_list',
    ),
    path('profile/', UserDetailView.as_view(), name='user_detail'),
]
