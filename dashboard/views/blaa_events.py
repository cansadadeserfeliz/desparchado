from dateutil.parser import parse
from django.urls import reverse
from django.views.generic import CreateView, TemplateView

from dashboard.mixins import SuperuserRequiredMixin
from dashboard.services import get_blaa_event, get_blaa_events_list
from events.forms import EventCreateForm
from events.models import Event, Organizer
from places.models import Place


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


class BlaaEventCreateView(SuperuserRequiredMixin, CreateView):
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
            event_category = ''
            if self.blaa_event_json['type_activity'] == 'Club de Lectura':
                event_category = Event.Category.LITERATURE
            elif self.blaa_event_json['type_activity'] == 'Concierto':
                event_category = Event.Category.ART

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
                    'category': event_category,
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
