from django.urls import path

from .views import PressArticleListView
from .views import PressArticleDetailView

app_name = 'news'
urlpatterns = [
    path(
        'articles',
        PressArticleListView.as_view(),
        name='press_article_list'
    ),
    path(
        'articles/<slug:slug>/',
        PressArticleDetailView.as_view(),
        name='press_article_detail'
    ),
]
