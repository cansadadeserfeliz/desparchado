from django.conf.urls import url

from django.views.generic import TemplateView
from .views import HuntingOfSnarkGameCreateView
from .views import HuntingOfSnarkGameDetailView
from .views import HuntingOfSnarkCriteriaListView

urlpatterns = [
    url(
        r'^hunting-of-snark/$',
        HuntingOfSnarkGameCreateView.as_view(),
        name='hunting_of_snark_create'
    ),
    url(
        r'^hunting-of-snark/criteria/$',
        HuntingOfSnarkCriteriaListView.as_view(),
        name='hunting_of_snark_criteria_list'
    ),
    url(
        r'^hunting-of-snark/lists/bbc-top-100/$',
        TemplateView.as_view(
            template_name='games/hunting_of_snark_bbc_top_100.html'
        ),
        name='hunting_of_snark_bbc_top_100'
    ),
    url(
        r'^hunting-of-snark/(?P<slug>[\w-]+)/$',
        HuntingOfSnarkGameDetailView.as_view(),
        name='hunting_of_snark_detail'
    ),
]
