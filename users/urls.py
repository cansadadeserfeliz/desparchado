from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import UserDetailView, UserCreationFormView
from .views import UserAddedEventsListView
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
    url(
        r'^register/$',
        UserCreationFormView.as_view(),
        name='register'
    ),
    url(
        r'^added-events/$',
        UserAddedEventsListView.as_view(),
        name='user_added_events_list',
    ),
    url(r'^(?P<slug>[\w-]+)/$', UserDetailView.as_view(), name='user_detail'),
]
