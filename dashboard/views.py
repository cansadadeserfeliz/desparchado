from django.views.generic import TemplateView
from django.views.generic import CreateView
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay
from django.db.models.functions import Cast
from django.db.models.fields import DateField
from django.core.urlresolvers import reverse
from django.utils import timezone

from events.models import Event
from events.models import Organizer
from events.models import Speaker
from events.models import SocialNetworkPost
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


class SocialPostsListView(SuperuserRequiredMixin, ListView):
    model = Event
    paginate_by = 100
    context_object_name = 'events'
    template_name = 'dashboard/social_posts.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.future()
        return queryset.order_by('event_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['published_social_posts'] = SocialNetworkPost.objects.filter(
            published_at__date__lte=timezone.now(),
        ).select_related('event').order_by('-published_at')[:25]
        context['future_social_posts'] = SocialNetworkPost.objects.filter(
            published_at__date__gt=timezone.now(),
        ).select_related('event').order_by('published_at')
        return context


class PlacesListView(SuperuserRequiredMixin, ListView):
    model = Place
    paginate_by = 300
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
        self.event = None

        blaa_slug = self.request.GET.get('blaa-slug', '')
        if blaa_slug:
            self.blaa_event_json = get_blaa_event(blaa_slug)

            self.event_source_url = 'http://www.banrepcultural.org{}'.format(
                self.blaa_event_json['path']
            )
            self.event = Event.objects.filter(
                event_source_url=self.event_source_url,
            ).first()
        else:
            self.blaa_event_json = None

        return super(EventCreateView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(EventCreateView, self).get_initial()

        if self.blaa_event_json:
            event_type = Event.EVENT_TYPE_PUBLIC_LECTURE
            if self.blaa_event_json['tipo'] == 'Taller':
                event_type = Event.EVENT_TYPE_MASTER_CLASS
            elif self.blaa_event_json['tipo'] == 'Visita guiada':
                event_type = Event.EVENT_TYPE_TOUR
            elif self.blaa_event_json['tipo'] == 'Club de Lectura':
                event_type = Event.EVENT_TYPE_MEETING
            elif self.blaa_event_json['tipo'] == 'Exposición':
                event_type = Event.EVENT_TYPE_EXHIBITION
            elif self.blaa_event_json['tipo'] == 'Concierto':
                event_type = Event.EVENT_TYPE_CONCERT
            elif self.blaa_event_json['tipo'] == 'Charla previa':
                event_type = Event.EVENT_TYPE_MEETING

            organizer = Organizer.objects.filter(name='Banco de la República').first()
            place = Place.objects.filter(name=self.blaa_event_json['place']).first()

            initial.update(dict(
                title=self.blaa_event_json['titulo'],
                event_type=event_type,
                topic=Event.EVENT_TOPIC_ART,
                event_source_url=self.event_source_url,
                organizer=organizer,
                place=place,
            ))
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blaa_event_json'] = self.blaa_event_json
        context['event'] = self.event
        return context

    def get_success_url(self):
        if self.object.is_published and self.object.is_approved:
            return self.object.get_absolute_url()
        else:
            return reverse('users:user_added_events_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_approved = True
        self.object.created_by = self.request.user
        self.object.save()

        return super().form_valid(form)
