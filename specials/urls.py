from django.urls import path

from .views import SpecialDetailView


app_name = 'specials'
urlpatterns = [
    path(
        '<slug:slug>/',
        SpecialDetailView.as_view(),
        name='special_detail'
    ),
]
