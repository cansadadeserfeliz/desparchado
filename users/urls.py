from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .forms import LoginForm, PasswordResetForm, SetPasswordForm
from .views import UserAddedEventsListView, UserCreationFormView, UserDetailView

app_name = 'users'
urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            authentication_form=LoginForm,
        ),
        name='login',
    ),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            email_template_name='users/password_reset_email.txt',
            html_email_template_name='users/password_reset_email.html',
            form_class=PasswordResetForm,
            success_url=reverse_lazy('users:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_change_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            form_class=SetPasswordForm,
            success_url=reverse_lazy('users:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    path(
        'register/',
        UserCreationFormView.as_view(),
        name='register',
    ),
    path(
        'added-events/',
        UserAddedEventsListView.as_view(),
        name='user_added_events_list',
    ),
    path('profile/', UserDetailView.as_view(), name='user_detail'),
]
