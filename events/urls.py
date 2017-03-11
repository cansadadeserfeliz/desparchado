from django.conf.urls import url

from .views import EventListView, EventDetailView


urlpatterns = [
    url(r'^$', EventListView.as_view(), name='event_list'),
    url(r'^(?P<pk>\d+)/$', EventDetailView.as_view(), name='event_detail'),
]
