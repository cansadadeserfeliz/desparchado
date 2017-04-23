from django.conf.urls import url

from .views import UserDetailView


urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/$', UserDetailView.as_view(), name='user_detail'),
]
