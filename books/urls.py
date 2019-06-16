from django.urls import path

from .views import BookDetailView


app_name = 'books'
urlpatterns = [
    path(
        '<slug:slug>/',
        BookDetailView.as_view(),
        name='book_detail'
    ),
]
