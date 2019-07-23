from django.urls import path

from .views import PressArticleListView

app_name = 'news'
urlpatterns = [
    path(
        'articles',
        PressArticleListView.as_view(),
        name='press_article_list'
    ),
]
