from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView, DetailView

from events.models import Event


class HomeView(TemplateView, UserPassesTestMixin):
    template_name = 'playground/home.html'

    def test_func(self):
        return self.request.user.is_superuser


class EventDetailView(DetailView, UserPassesTestMixin):
    template_name = 'playground/event_detail.html'
    model = Event

    def test_func(self):
        return self.request.user.is_superuser
