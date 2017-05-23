from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import UserDetailView
from .forms import LoginForm


urlpatterns = [
    url(
        r'^login/$',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            authentication_form=LoginForm,
        ),
        name='login'
    ),
    url(r'^(?P<slug>[\w-]+)/$', UserDetailView.as_view(), name='user_detail'),
]
