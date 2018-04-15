from django.views.generic import TemplateView
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.db.models import Count

from events.models import Event
from events.models import Organizer
from events.models import Speaker
from places.models import Place


User = get_user_model()


class SuperuserRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser


class HomeView(SuperuserRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_events_count'] = Event.objects.published().count()
        context['future_events_count'] = Event.objects.published().future().count()
        context['places_count'] = Place.objects.count()
        context['organizers_count'] = Organizer.objects.count()
        context['speakers_count'] = Speaker.objects.count()
        context['active_users_count'] = User.objects.filter(is_active=True).count()
        return context


class EventsListView(SuperuserRequiredMixin, ListView):
    model = Event
    paginate_by = 50
    context_object_name = 'events'
    template_name = 'dashboard/events.html'
    ordering = '-modified'


class PlacesListView(SuperuserRequiredMixin, ListView):
    model = Place
    paginate_by = 50
    context_object_name = 'places'
    template_name = 'dashboard/places.html'


class UsersListView(SuperuserRequiredMixin, ListView):
    model = User
    paginate_by = 50
    context_object_name = 'users'
    template_name = 'dashboard/users.html'

    def get_queryset(self):
        queryset = User.objects.annotate(events_count=Count('created_events'))
        return queryset


