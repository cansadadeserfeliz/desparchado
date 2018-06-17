from django.views.generic import TemplateView
from django.views.generic import CreateView
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay
from django.db.models.functions import Cast
from django.db.models.fields import DateField
from django.shortcuts import redirect
from django.contrib import messages

from events.models import Event
from events.models import Organizer
from events.models import Speaker
from events.forms import EventCreateForm
from places.models import Place
from dashboard.models import EventSource
from dashboard.services import get_blaa_events_list
from dashboard.services import get_blaa_event


User = get_user_model()


class SuperuserRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser


class HomeView(SuperuserRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_events_count'] = Event.objects.published().count()
        context['future_events'] = Event.objects.published().future().all()
        context['future_events_count'] = Event.objects.published().future().count()
        context['future_events_by_date'] = Event.objects.published().future()\
            .annotate(day=Cast('event_date', DateField())).values('day') \
            .annotate(count=Count('day')).values('day', 'count')\
            .order_by('day')
        context['future_events_by_weekday'] = Event.objects.published().future()\
            .annotate(weekday=ExtractWeekDay('event_date')).values('weekday')\
            .annotate(count=Count('id')).values('weekday', 'count')\
            .order_by('weekday')
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
        queryset = User.objects.annotate(
            events_count=Count('created_events'),
        ).order_by('-last_login')
        return queryset


class EventSourceListView(SuperuserRequiredMixin, ListView):
    model = EventSource
    paginate_by = 50
    template_name = 'dashboard/event_sources.html'
    context_object_name = 'event_sources'
    ordering = '-modified'


class BlaaEventsListView(TemplateView):
    template_name = 'dashboard/blaa/events_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = get_blaa_events_list()
        return context


class EventCreateView(CreateView):
    form_class = EventCreateForm
    template_name = 'dashboard/event_form.html'

    def dispatch(self, request, *args, **kwargs):

        blaa_slug = self.request.GET.get('blaa-slug', '')
        if blaa_slug:
            self.blaa_event_json = get_blaa_event(blaa_slug)
        else:
            self.blaa_event_json = None

        return super(EventCreateView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(EventCreateView, self).get_initial()

        if self.blaa_event_json:
            event_url = 'http://www.banrepcultural.org{}'.format(
                self.blaa_event_json['path']
            )
            if Event.objects.filter(event_source_url=event_url).exists():
                messages.add_message(self.request, messages.INFO, 'Event exists.')
                return redirect('blaa_events_list')

            event_type = Event.EVENT_TYPE_PUBLIC_LECTURE
            if self.blaa_event_json['tipo'] == 'Taller':
                event_type = Event.EVENT_TYPE_MASTER_CLASS

            organizer = Organizer.objects.filter(name='Banco de la República').first()

            initial.update(dict(
                title=self.blaa_event_json['titulo'],
                event_type=event_type,
                event_source_url=event_url,
                organizer=organizer,
            ))
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blaa_event_json'] = self.blaa_event_json
        return context
