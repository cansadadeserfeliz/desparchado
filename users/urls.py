from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from .views import UserDetailView, UserCreationFormView
from .views import UserAddedEventsListView
from .forms import LoginForm
from .forms import PasswordResetForm
from .forms import SetPasswordForm


urlpatterns = [
    url(
        r'^login/$',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            authentication_form=LoginForm,
        ),
        name='login',
    ),

    url(
        r'^password_reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            email_template_name='users/password_reset_email.html',
            form_class=PasswordResetForm,
            success_url=reverse_lazy('users:password_reset_done'),
        ),
        name='password_reset',
    ),
    url(
        r'^password_reset/done/$',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_change_done.html',
        ),
        name='password_reset_done',
    ),
    url(
        r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            form_class=SetPasswordForm,
            success_url=reverse_lazy('users:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    url(
        r'^reset/done/$',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),

    url(
        r'^register/$',
        UserCreationFormView.as_view(),
        name='register',
    ),
    url(
        r'^added-events/$',
        UserAddedEventsListView.as_view(),
        name='user_added_events_list',
    ),
    url(r'^(?P<slug>[\w-]+)/$', UserDetailView.as_view(), name='user_detail'),
]
