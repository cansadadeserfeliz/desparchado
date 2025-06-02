from dateutil.parser import parse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.db.models.fields import DateField
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, FormView, ListView, TemplateView

from dashboard.forms import FilboEventCreateForm
from dashboard.services import get_blaa_event, get_blaa_events_list, sync_filbo_events
from events.forms import EventCreateForm
from events.models import Event, Organizer, SocialNetworkPost, Speaker
from places.models import Place

User = get_user_model()


class SuperuserRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser


class HomeView(SuperuserRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['future_events'] = Event.objects.published().future().all()
        context['future_events_count'] = Event.objects.published().future().count()

        context['future_events_by_date'] = (
            Event.objects.published()
            .future()
            .annotate(day=Cast('event_date', DateField()))
            .values('day')
            .annotate(count=Count('day'))
            .values('day', 'count')
            .order_by('day')
        )

        context['all_filbo_2025_events_count'] = Event.objects.filter(
            filbo_id__isnull=False,
            event_date__year=2025,
        ).count()
        context['published_filbo_2025_events_count'] = (
            Event.objects.published()
            .filter(
                filbo_id__isnull=False,
                event_date__year=2025,
            )
            .count()
        )

        context['organizers_count'] = Organizer.objects.count()
        context['speakers_count'] = Speaker.objects.count()
        context['speakers_filbo_2025_count'] = (
            Speaker.objects.filter(
                events__filbo_id__isnull=False,
                events__event_date__year=2025,
            )
            .distinct()
            .count()
        )
        context['speakers_without_image_count'] = Speaker.objects.filter(
            image='',
        ).count()
        context['active_users_count'] = User.objects.filter(is_active=True).count()
        context['places_count'] = Place.objects.count()
        return context


class SocialPostsListView(SuperuserRequiredMixin, TemplateView):
    template_name = 'dashboard/social_posts.html'


def social_events_source(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    event_list = []

    start_date = parse(start_date)
    end_date = parse(end_date)

    blue = '#0073b7'
    green = '#00a65a'
    muted = '#777777'

    events = (
        Event.objects.published()
        .filter(
            event_date__date__range=(start_date, end_date),
        )
        .prefetch_related('social_posts')
        .order_by('event_date')
        .all()
    )
    for event in events:
        if event.social_posts.exists():
            color = green
        else:
            color = muted
        local_date = timezone.localtime(event.event_date)
        event_list.append(
            {
                'title': event.title,
                'start': local_date.isoformat(),
                'backgroundColor': color,
                'borderColor': color,
                'url': reverse('admin:events_event_change', args=(event.id,)),
                'imageUrl': event.get_image_url(),
            },
        )

    social_posts = (
        SocialNetworkPost.objects.filter(
            published_at__range=(start_date, end_date),
        )
        .select_related('event', 'created_by')
        .all()
    )

    for social_post in social_posts:
        local_date = timezone.localtime(social_post.published_at)
        event_list.append(
            {
                'title': social_post.event.title,
                'start': local_date.isoformat(),
                'backgroundColor': blue,
                'borderColor': blue,
                'url': reverse(
                    'admin:events_event_change', args=(social_post.event.id,),
                ),
                'imageUrl': social_post.event.get_image_url(),
            },
        )

    return JsonResponse(event_list, safe=False)


class PlacesListView(SuperuserRequiredMixin, ListView):
    model = Place
    paginate_by = 300
    context_object_name = 'places'
    template_name = 'dashboard/places.html'


class BlaaEventsListView(SuperuserRequiredMixin, TemplateView):
    template_name = 'dashboard/blaa/events_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        events, pages_count = get_blaa_events_list(page=page)

        for event_data in events:
            blaa_slug = event_data.get('contenido_url', '')
            if blaa_slug:
                event_source_url = f'http://www.banrepcultural.org{blaa_slug}'
                event = Event.objects.filter(
                    event_source_url=event_source_url,
                ).first()
                if event:
                    event_data['desparchado_event'] = event

        context['events'] = events
        context['pages'] = range(1, pages_count + 1)
        context['current_page'] = int(page)
        return context


class EventCreateView(SuperuserRequiredMixin, CreateView):
    form_class = EventCreateForm
    template_name = 'dashboard/event_form.html'
    blaa_event_json = None
    event_source_url = ''
    event = None

    def dispatch(self, request, *args, **kwargs):
        self.event = None

        blaa_slug = self.request.GET.get('blaa-slug', '')
        if blaa_slug:
            self.blaa_event_json = get_blaa_event(event_slug=blaa_slug)

            self.event_source_url = (
                f"http://www.banrepcultural.org{self.blaa_event_json['path']}"
            )
            self.event = Event.objects.filter(
                event_source_url=self.event_source_url,
            ).first()
        else:
            self.blaa_event_json = None

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()

        if self.blaa_event_json:
            event_type = Event.EVENT_TYPE_PUBLIC_LECTURE
            if self.blaa_event_json['type_activity'] == 'Taller':
                event_type = Event.EVENT_TYPE_MASTER_CLASS
            elif self.blaa_event_json['type_activity'] == 'Visita guiada':
                event_type = Event.EVENT_TYPE_TOUR
            elif self.blaa_event_json['type_activity'] == 'Club de Lectura':
                event_type = Event.EVENT_TYPE_MEETING
            elif self.blaa_event_json['type_activity'] == 'Exposición':
                event_type = Event.EVENT_TYPE_EXHIBITION
            elif self.blaa_event_json['type_activity'] == 'Concierto':
                event_type = Event.EVENT_TYPE_CONCERT
            elif self.blaa_event_json['type_activity'] == 'Charla previa':
                event_type = Event.EVENT_TYPE_MEETING

            start_date = parse(self.blaa_event_json.get('date'))

            organizer = Organizer.objects.filter(name='Banco de la República').first()
            if self.blaa_event_json['place']:
                place = Place.objects.filter(
                    name__icontains=self.blaa_event_json['place'],
                ).first()
            else:
                place = None

            initial.update(
                {
                    'title': self.blaa_event_json['title'],
                    'event_type': event_type,
                    'topic': Event.EVENT_TOPIC_ART,
                    'event_source_url': self.event_source_url,
                    'event_date': start_date,
                    'description': self.blaa_event_json.get('body', '')
                    + '\n\n'
                    + self.blaa_event_json.get('horarios', '')
                    + '\n\n'
                    + self.blaa_event_json.get('description', '')
                    + '\n\n'
                    + self.blaa_event_json.get('notes', ''),
                    'organizers': [organizer],
                    'place': place,
                },
            )
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blaa_event_json'] = self.blaa_event_json
        context['event'] = self.event
        return context

    def get_success_url(self):
        if self.object.is_published and self.object.is_approved:
            return self.object.get_absolute_url()

        return reverse('users:user_added_events_list')

    def form_valid(self, form):
        # pylint: disable=attribute-defined-outside-init
        self.object = form.save(commit=False)
        self.object.is_approved = True
        self.object.created_by = self.request.user
        self.object.save()

        return super().form_valid(form)


class FilboEventFormView(SuperuserRequiredMixin, FormView):
    form_class = FilboEventCreateForm
    template_name = 'dashboard/filbo/events_form.html'
    success_url = reverse_lazy('dashboard:filbo_event_form')

    def form_valid(self, form):
        sync_filbo_events(
            spreadsheet_id=form.cleaned_data['spreadsheet_id'],
            worksheet_number=form.cleaned_data['worksheet_number'],
            worksheet_range=form.cleaned_data['worksheet_range'],
            request_user=self.request.user,
        )

        return super().form_valid(form)
