from dateutil.parser import parse

from django.utils import timezone
from django.views.generic import TemplateView, CreateView, ListView, FormView
from django.http import JsonResponse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay, Cast
from django.db.models.fields import DateField
from django.urls import reverse, reverse_lazy

from events.models import Event, Organizer, Speaker, SocialNetworkPost
from events.forms import EventCreateForm
from places.models import Place
from dashboard.services import get_blaa_events_list, get_blaa_event, sync_filbo_events
from dashboard.forms import FilboEventCreateForm


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
        context['future_events_by_date'] = Event.objects.published().future()\
            .annotate(day=Cast('event_date', DateField())).values('day') \
            .annotate(count=Count('day')).values('day', 'count')\
            .order_by('day')
        context['future_events_by_weekday'] = Event.objects.published().future()\
            .annotate(weekday=ExtractWeekDay('event_date')).values('weekday')\
            .annotate(count=Count('id')).values('weekday', 'count')\
            .order_by('weekday')
        context['organizers_count'] = Organizer.objects.count()
        context['speakers_count'] = Speaker.objects.count()
        context['active_users_count'] = User.objects.filter(is_active=True).count()
        return context


class SocialPostsListView(SuperuserRequiredMixin, TemplateView):
    template_name = 'dashboard/social_posts.html'


def social_events_source(request):
    """
    Returns a JSON response with event and social post entries for a specified date range.
    
    This view parses the 'start' and 'end' parameters from the GET query to determine the date range.
    It retrieves published events occurring within this period and assigns a green color if the event
    has associated social posts or a muted color if not. Additionally, it retrieves published social
    network posts within the same range, assigning them a blue color. Each entry in the response
    includes the event title, local start time in ISO format, background and border colors, a URL for
    admin editing, and an image URL. The aggregated list is returned as a JSON response.
    """
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    event_list = []

    start_date = parse(start_date)
    end_date = parse(end_date)

    blue = '#0073b7'
    green = '#00a65a'
    muted = '#777777'

    events = Event.objects.published().filter(
        event_date__date__range=(start_date, end_date),
    ).prefetch_related('social_posts').order_by('event_date').all()
    for event in events:
        if event.social_posts.exists():
            color = green
        else:
            color = muted
        local_date = timezone.localtime(event.event_date)
        event_list.append(dict(
            title=event.title,
            start=local_date.isoformat(),
            backgroundColor=color,
            borderColor=color,
            url=reverse('admin:events_event_change', args=(event.id,)),
            imageUrl=event.get_image_url(),
        ))

    social_posts = SocialNetworkPost.objects.filter(
        published_at__range=(start_date, end_date),
    ).select_related('event', 'created_by').all()

    for social_post in social_posts:
        local_date = timezone.localtime(social_post.published_at)
        event_list.append(dict(
            title=social_post.event.title,
            start=local_date.isoformat(),
            backgroundColor=blue,
            borderColor=blue,
            url=reverse('admin:events_event_change', args=(social_post.event.id,)),
            imageUrl=social_post.event.get_image_url(),
        ))

    return JsonResponse(event_list, safe=False)


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
        """
        Return users annotated with event counts, ordered by last login.
        
        Retrieves a queryset where each user object is annotated with the count of its related
        'created_events' and sorted in descending order by the user's last login timestamp.
        """
        queryset = User.objects.annotate(
            events_count=Count('created_events'),
        ).order_by('-last_login')
        return queryset


class BlaaEventsListView(SuperuserRequiredMixin, TemplateView):
    template_name = 'dashboard/blaa/events_list.html'

    def get_context_data(self, **kwargs):
        """
        Enhance context with paginated Blaa events and enriched event details.
        
        Retrieves the current page from the query parameters (defaulting to 1) and obtains
        a list of Blaa events along with the total page count using get_blaa_events_list.
        For each event, if a source slug ('contenido_url') is available, constructs an event
        source URL and checks the database for a matching Event. If found, the Event is added
        to the event data under 'desparchado_event'. Updates the context with the events list,
        a pagination range, and the current page number.
        """
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        events, pages_count = get_blaa_events_list(page=page)

        for event_data in events:
            blaa_slug = event_data.get('contenido_url', '')
            if blaa_slug:
                event_source_url = 'http://www.banrepcultural.org{}'.format(
                    blaa_slug
                )
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

    def dispatch(self, request, *args, **kwargs):
        self.event = None

        blaa_slug = self.request.GET.get('blaa-slug', '')
        if blaa_slug:
            self.blaa_event_json = get_blaa_event(event_slug=blaa_slug)

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

            organizer = Organizer.objects.filter(
                name='Banco de la República'
            ).first()
            if self.blaa_event_json['place']:
                place = Place.objects.filter(
                    name__icontains=self.blaa_event_json['place']
                ).first()
            else:
                place = None

            initial.update(dict(
                title=self.blaa_event_json['title'],
                event_type=event_type,
                topic=Event.EVENT_TOPIC_ART,
                event_source_url=self.event_source_url,
                event_date=start_date,
                description=
                self.blaa_event_json.get('body', '') + '\n\n' +
                self.blaa_event_json.get('horarios', '') + '\n\n' +
                self.blaa_event_json.get('description', '') + '\n\n' +
                self.blaa_event_json.get('notes', ''),
                organizers=[organizer],
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
        """
        Validates and saves form data by marking the object as approved.
        
        This method creates a new object from the submitted form data without committing
        it immediately. It sets the object's approval status to True and assigns the current
        user as the creator before saving the object. It then delegates to the superclass's
        form_valid method to complete the processing and return an HTTP response.
        
        Args:
            form: The validated form instance containing the data to save.
        
        Returns:
            An HTTP response from the superclass's form_valid method.
        """
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
        """
        Synchronizes Filbo events using validated spreadsheet data.
        
        Extracts the spreadsheet ID, worksheet number, and worksheet range from the form's
        cleaned data and calls sync_filbo_events to update event information. Delegates to
        the superclass's form_valid method to continue form processing.
        
        Args:
            form: A Django form instance containing the spreadsheet parameters.
        
        Returns:
            The HTTP response returned by the superclass's form_valid method.
        """
        sync_filbo_events(
            spreadsheet_id=form.cleaned_data['spreadsheet_id'],
            worksheet_number=form.cleaned_data['worksheet_number'],
            worksheet_range=form.cleaned_data['worksheet_range'],
            request_user=self.request.user,
        )

        return super().form_valid(form)
