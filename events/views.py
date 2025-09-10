from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.cache import cache
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from desparchado.autocomplete import BaseAutocomplete
from desparchado.mixins import EditorPermissionRequiredMixin
from desparchado.utils import send_notification
from places.models import City

from .forms import EventCreateForm, EventUpdateForm, OrganizerForm, SpeakerForm
from .models import Event, Organizer, Speaker


class EventListBaseView(ListView):
    model = Event
    context_object_name = 'events'
    paginate_by = 15
    search_query_name = 'q'
    search_query_value = ''
    search_query_min_length = 3
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
        context['search_query_name'] = self.search_query_name
        context['search_query_value'] = self.search_query_value
        context['city_filter_name'] = self.city_filter_name
        context['city_filter_value'] = self.city_filter_value
        context['category_filter_name'] = self.category_filter_name
        context['category_filter_value'] = self.category_filter_value
        context['category_choices'] = Event.Category.choices

        params = {}
        if self.search_query_value:
            params[self.search_query_name] = self.search_query_value
        if self.city_filter_value:
            params[self.city_filter_name] = self.city_filter_value
        if self.category_filter_value:
            params[self.category_filter_name] = self.category_filter_value
        context['pagination_query_params'] = f"&{urlencode(params)}" if params else ''

        return context

    def get_queryset(self):
        queryset = Event.objects.published()

        if self.city:
            queryset = queryset.filter(place__city=self.city)

        if self.category_filter_value:
            queryset = queryset.filter(category=self.category_filter_value)

        if (
            self.search_query_value
            and len(self.search_query_value) >= self.search_query_min_length
        ):
            queryset = (
                queryset.annotate(
                    search=SearchVector('title', 'description', 'speakers__name'),
                )
                .filter(
                    Q(title__unaccent__icontains=self.search_query_value)
                    | Q(description__unaccent__icontains=self.search_query_value)
                    | Q(speakers__name__unaccent__icontains=self.search_query_value)
                    | Q(search=SearchQuery(self.search_query_value)),
                )
            )

        return (queryset
                .select_related('place')
                .prefetch_related('speakers')
                .order_by('event_date')
                .distinct())


class EventListView(EventListBaseView):
    template_name = 'events/event_list.html'

    def get_queryset(self):
        return super().get_queryset().future()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'city_filter_ids' in cache:
            city_ids = cache.get('city_filter_ids')
        else:
            events = self.get_queryset()
            city_ids = events.values_list("place__city_id", flat=True)
            cache.set('city_filter_ids', city_ids, 24 * 60 * 60)

        context['cities'] = City.objects.filter(id__in=city_ids)

        return context

class PastEventListView(EventListBaseView):
    template_name = "events/past_event_list.html"
    year_filter_name = 'year'
    year_filter_value = None
    year_range = []

    def dispatch(self, request, *args, **kwargs):
        self.year_filter_value = request.GET.get(self.year_filter_name, None)
        self.year_range = list(map(str, range(2017, now().year + 1)))

        if self.year_filter_value not in self.year_range:
            self.year_filter_value = None
        try:
            self.year_filter_value = int(self.year_filter_value)
        except (ValueError, TypeError):
            self.year_filter_value = None

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().past()

        if self.year_filter_value:
            queryset = queryset.filter(event_date__year=self.year_filter_value)

        return queryset.order_by('-event_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # For search form rendering
        context["cities"] = City.objects.all()
        context['year_filter_name'] = self.year_filter_name
        context['year_filter_value'] = self.year_filter_value
        context['year_range'] = self.year_range

        if self.year_filter_value:
            params = {self.year_filter_name: self.year_filter_value}
            context['pagination_query_params'] += f"&{urlencode(params)}"

        return context


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
        context['events'] = (
            self.get_object().events.published()
            .future()
            .select_related('place')
            .all()[:30]
        )
        context["past_events"] = (
            self.get_object()
            .events.published()
            .past()
            .order_by("-event_date")
            .select_related("place")
            .prefetch_related("speakers")
            .all()[:30]
        )
        return context


class SpeakerDetailView(DetailView):
    model = Speaker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        speaker = self.get_object()
        context["events"] = (
            speaker.events.published()
            .future()
            .select_related("place")
            .prefetch_related("speakers")
            .all()[:30]
        )
        context['past_events'] = (
            speaker.events.published()
            .past()
            .order_by('-event_date')
            .select_related('place')
            .prefetch_related('speakers')
            .all()[:9]
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
