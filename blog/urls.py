from django.urls import path

from .views import PostDetailView, PostListView

app_name = 'blog'
urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
]
