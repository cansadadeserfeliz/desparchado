from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin


class SuperuserRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser


from events.models import Event


class HomeView(SuperuserRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_events_count'] = Event.objects.published().count()
        context['future_events_count'] = Event.objects.published().future().count()
        return context
