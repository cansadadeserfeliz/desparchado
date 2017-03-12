from django.conf.urls import url

from .views import PlaceListView, PlaceDetailView


urlpatterns = [
    url(r'^$', PlaceListView.as_view(), name='place_list'),
    url(r'^(?P<pk>\d+)/$', PlaceDetailView.as_view(), name='place_detail'),
]
