from django.conf.urls import url

from .views import EventDetailView


urlpatterns = [
    url(r'^(?P<pk>\d+)/$', EventDetailView.as_view(), name='event_detail'),
]
