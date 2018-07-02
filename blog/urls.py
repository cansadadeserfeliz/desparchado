from django.conf.urls import url

from .views import PostListView
from .views import PostDetailView

urlpatterns = [
    url(
        r'^$',
        PostListView.as_view(),
        name='post_list'
    ),
    url(
        r'^(?P<slug>[\w-]+)/$',
        PostDetailView.as_view(),
        name='post_detail'
    ),
]
