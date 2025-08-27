from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView

from events.models import Event


class HomeView(TemplateView, UserPassesTestMixin):
    template_name = 'playground/home.html'

    def test_func(self):
        return self.request.user.is_superuser


class EventDetailView(TemplateView, UserPassesTestMixin):
    template_name = 'playground/event_detail.html'
    model = Event

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['event'] = Event.objects.order_by('?').first()
        return context
