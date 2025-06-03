from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView


class HomeView(TemplateView, UserPassesTestMixin):
    template_name = 'playground/home.html'

    def test_func(self):
        return self.request.user.is_superuser
