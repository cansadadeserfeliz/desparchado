from django.urls import path

from django.views.generic import TemplateView


app_name = 'history'
urlpatterns = [
    path(
        '',
        TemplateView.as_view(template_name=''),
        name='home'
    ),
]
