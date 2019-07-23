from django.urls import path

from .views import BookDetailView
from .views import BookListView
from .views import HomeTemplateView


app_name = 'books'
urlpatterns = [
    path(
        '',
        HomeTemplateView.as_view(),
        name='home'
    ),
    path(
        'list/',
        BookListView.as_view(),
        name='book_list'
    ),
    path(
        '<slug:slug>/',
        BookDetailView.as_view(),
        name='book_detail'
    ),
]
