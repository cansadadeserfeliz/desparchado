from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from desparchado.autocomplete import BaseAutocomplete
from desparchado.mixins import EditorPermissionRequiredMixin
from desparchado.utils import send_notification
from places.models import City

from .forms import EventCreateForm, EventUpdateForm, OrganizerForm, SpeakerForm
from .models import Event, Organizer, Speaker


class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    paginate_by = 15
    search_query_name = 'q'
    search_query_value = ''
    city_filter_name = 'city'
    city_filter_value = ''
    city = None
    category_filter_name = 'category'
    category_filter_value = ''

    def dispatch(self, request, *args, **kwargs):
        self.search_query_value = request.GET.get(self.search_query_name, '')
        self.city_filter_value = request.GET.get(self.city_filter_name)
        self.category_filter_value = request.GET.get(self.category_filter_name)

        if self.city_filter_value:
            self.city = City.objects.filter(slug=self.city_filter_value).first()

        if self.category_filter_value not in Event.Category:
            self.category_filter_value = ''

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # For search form rendering
        context['city_filter_name'] = self.city_filter_name
        context['city_filter_value'] = self.city_filter_value
        context['category_filter_name'] = self.category_filter_name
        context['category_filter_value'] = self.category_filter_value
        context['category_choices'] = Event.Category.choices
        context['cities'] = City.objects.all()

        context['pagination_query_params'] = ''
        if self.search_query_value:
            context['pagination_query_params'] += \
                f'&{self.search_query_name}={escape(self.search_query_value)}'
        if self.city_filter_value:
            context['pagination_query_params'] += \
                f'&{self.city_filter_name}={escape(self.city_filter_value)}'
        if self.category_filter_value:
            context['pagination_query_params'] += \
                f'&{self.category_filter_name}={self.category_filter_value}'

        return context

    def get_queryset(self):
        queryset = Event.objects.published().future()

        if self.city:
            queryset = queryset.filter(place__city=self.city)

        if self.category_filter_value:
            queryset = queryset.filter(category=self.category_filter_value)

        if self.search_query_value and len(self.search_query_value) > 3:
            queryset = (
                queryset.annotate(unaccent_title=SearchVector('title__unaccent'))
                .annotate(unaccent_description=SearchVector('description__unaccent'))
                .annotate(
                    speakers_names=SearchVector(
                        StringAgg('speakers__name', delimiter=' '),
                    ),
                )
                .annotate(
                    unaccent_speakers_names=SearchVector(
                        StringAgg('speakers__name__unaccent', delimiter=' '),
                    ),
                )
                .annotate(
                    search=SearchVector(
                        'title',
                        'unaccent_title',
                        'description',
                        'unaccent_description',
                        'speakers_names',
                        'unaccent_speakers_names',
                    ),
                )
                .filter(
                    Q(title__icontains=self.search_query_value)
                    | Q(unaccent_title__icontains=self.search_query_value)
                    | Q(description__icontains=self.search_query_value)
                    | Q(unaccent_description__icontains=self.search_query_value)
                    | Q(speakers_names__icontains=self.search_query_value)
                    | Q(unaccent_speakers_names__icontains=self.search_query_value)
                    | Q(search=SearchQuery(self.search_query_value)),
                )
            )

        return (queryset
                .select_related('place')
                .prefetch_related('speakers')
                .order_by('event_date')
                .distinct())


class PastEventListView(ListView):
    model = Event
    context_object_name = 'events'
    template_name = 'events/past_event_list.html'
    paginate_by = 18

    def get_queryset(self):
        queryset = Event.objects.published().past().order_by('-event_date')
        return queryset.select_related('place')


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'

    def get_queryset(self):
        return (
            Event.objects.published()
            .select_related(
                'place',
            )
            .all()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_events'] = (
            Event.objects.exclude(id=self.object.id)
            .published()
            .future()
            .select_related('place')
            .order_by('?')[:3]
        )
        context['organizers'] = list(self.object.organizers.all())
        context['speakers'] = list(self.object.speakers.all())
        return context


class OrganizerListView(ListView):
    model = Organizer
    context_object_name = 'organizers'
    paginate_by = 20


class OrganizerDetailView(DetailView):
    model = Organizer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.get_object().events.published().future().all()[:30]
        context['past_events'] = (
            self.get_object()
            .events.published()
            .past()
            .order_by('-event_date')
            .all()[:30]
        )
        return context


class SpeakerDetailView(DetailView):
    model = Speaker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        speaker = self.get_object()
        context['events'] = speaker.events.published().future().all()[:30]
        context['past_events'] = (
            speaker.events.published().past().order_by('-event_date').all()[:9]
        )
        return context


class SpeakerListView(ListView):
    model = Speaker
    context_object_name = 'speakers'
    paginate_by = 54
    ordering = 'name'
    q = ''

    def dispatch(self, request, *args, **kwargs):
        self.q = request.GET.get('q', '')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.q:
            queryset = queryset.annotate(
                unaccent_name=SearchVector('name__unaccent'),
            ).filter(Q(name__icontains=self.q) | Q(unaccent_name__icontains=self.q))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_string'] = self.q
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    form_class = EventCreateForm
    model = Event

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

        send_notification(self.request, self.object, 'event', True)
        return super().form_valid(form)


class EventUpdateView(EditorPermissionRequiredMixin, UpdateView):
    form_class = EventUpdateForm
    model = Event
    context_object_name = 'event'

    def get_success_url(self):
        if self.object.is_published and self.object.is_approved:
            return self.object.get_absolute_url()

        return reverse('users:user_added_events_list')

    def form_valid(self, form):
        send_notification(self.request, self.object, 'event', False)
        return super().form_valid(form)


class OrganizerCreateView(LoginRequiredMixin, CreateView):
    model = Organizer
    form_class = OrganizerForm

    def form_valid(self, form):
        # pylint: disable=attribute-defined-outside-init
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()

        send_notification(self.request, self.object, 'organizer', True)
        return super().form_valid(form)


class OrganizerUpdateView(EditorPermissionRequiredMixin, UpdateView):
    model = Organizer
    form_class = OrganizerForm

    def form_valid(self, form):
        send_notification(self.request, self.object, 'organizer', False)
        return super().form_valid(form)


class SpeakerCreateView(LoginRequiredMixin, CreateView):
    model = Speaker
    form_class = SpeakerForm

    def form_valid(self, form):
        # pylint: disable=attribute-defined-outside-init
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()

        send_notification(self.request, self.object, 'speaker', True)
        return super().form_valid(form)


class SpeakerUpdateView(EditorPermissionRequiredMixin, UpdateView):
    model = Speaker
    form_class = SpeakerForm

    def form_valid(self, form):
        send_notification(self.request, self.object, 'speaker', False)
        return super().form_valid(form)


class OrganizerAutocomplete(BaseAutocomplete):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor!
        if not self.request.user.is_authenticated:
            return Organizer.objects.none()

        qs = Organizer.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__unaccent__icontains=self.q)

        return qs


class SpeakerAutocomplete(BaseAutocomplete):

    def get_result_label(self, result):
        return format_html(
            '<img src="{}" height="30"> {}', result.get_image_url(), result.name,
        )

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor!
        if not self.request.user.is_authenticated:
            return Speaker.objects.none()

        qs = Speaker.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__unaccent__icontains=self.q)

        return qs


class OrganizerSuggestionsView(View):
    def get(self, request):
        query = request.GET.get('query', '')
        suggestion = None
        if len(query) >= 5:
            organizers = Organizer.objects.filter(
                name__unaccent__icontains=query,
            )[:3]
            if organizers:
                duplicated_organizers = ', '.join(
                    [
                        f'<a href="{organizer.get_absolute_url()}">'
                        f'{escape(organizer.name)}</a>'
                        for organizer in organizers
                    ],
                )

                suggestion = mark_safe(  # noqa: S308
                    'Advertencia para evitar agregar organizadores duplicados: '
                    f'ya existe(n) organizador(es) {duplicated_organizers}.',
                )

        return JsonResponse({'suggestion': suggestion})
