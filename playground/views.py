# ruff: noqa: S311
from random import randint

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView

from events.models import Event


class HomeView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'playground/home.html'

    def test_func(self):
        return self.request.user.is_superuser


class EventDetailView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'playground/event_detail.html'
    model = Event

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        count = Event.objects.count()
        context['event'] = Event.objects.all()[randint(0, count - 1)] if count else None
        return context
