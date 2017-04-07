from django.conf.urls import url

from .views import EventListView, EventDetailView, OrganizerListView


urlpatterns = [
    url(r'^$', EventListView.as_view(), name='event_list'),
    url(r'^(?P<pk>\d+)/$', EventDetailView.as_view(), name='event_detail'),
    url(r'^(?P<slug>[\w-]+)/$', EventDetailView.as_view(), name='event_detail'),

    url(r'organizations/^$', OrganizerListView.as_view(), name='organizer_list'),
]
