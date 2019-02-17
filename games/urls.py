from django.urls import path

from django.views.generic import TemplateView
from .views import HuntingOfSnarkGameCreateView
from .views import HuntingOfSnarkGameDetailView
from .views import HuntingOfSnarkCriteriaListView
from .views import HuntingOfSnarkGameListView

app_name = 'games'
urlpatterns = [
    path(
        'snark/',
        HuntingOfSnarkGameCreateView.as_view(),
        name='hunting_of_snark_create'
    ),
    path(
        'snark/criteria/',
        HuntingOfSnarkCriteriaListView.as_view(),
        name='hunting_of_snark_criteria_list'
    ),
    path(
        'snark/all/',
        HuntingOfSnarkGameListView.as_view(),
        name='hunting_of_snark_games_list'
    ),
    path(
        'snark/lists/bbc-top-100/',
        TemplateView.as_view(
            template_name='games/hunting_of_snark_bbc_top_100.html'
        ),
        name='hunting_of_snark_bbc_top_100'
    ),
    path(
        'snark/<slug:slug>/',
        HuntingOfSnarkGameDetailView.as_view(),
        name='hunting_of_snark_detail'
    ),
]
