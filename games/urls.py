from django.conf.urls import url

from .views import HuntingOfSnarkGameCreateView
from .views import HuntingOfSnarkGameDetailView

urlpatterns = [
    url(
        r'^hunting-of-snark/$',
        HuntingOfSnarkGameCreateView.as_view(),
        name='hunting_of_snark_create'
    ),
    url(
        r'^hunting-of-snark/(?P<slug>[\w-]+)/$',
        HuntingOfSnarkGameDetailView.as_view(),
        name='hunting_of_snark_detail'
    ),
]
