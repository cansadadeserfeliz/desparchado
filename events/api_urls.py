from django.urls import path

from events.api.views import EventListAPIView


app_name = 'events'
urlpatterns = [
    path(
        route='events/',
        view=EventListAPIView.as_view(),
        name='flavors_list'
    ),
]
