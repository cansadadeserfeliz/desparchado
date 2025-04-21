from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin


class HomeView(TemplateView, UserPassesTestMixin):
    template_name = 'playground/home.html'

    def test_func(self):
        return self.request.user.is_superuser
