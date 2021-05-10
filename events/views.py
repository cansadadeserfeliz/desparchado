from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import JsonResponse

from dal import autocomplete

from desparchado.utils import send_notification
from desparchado.mixins import EditorPermissionRequiredMixin
from places.models import City
from .models import Event, Organizer, Speaker
from .services import get_event_press_articles
from .forms import EventCreateForm
from .forms import EventUpdateForm
from .forms import OrganizerForm
from .forms import SpeakerForm


class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    paginate_by = 27
    city = None

    def dispatch(self, request, *args, **kwargs):

        self.city_slug_filter = request.GET.get('city')
        if self.city_slug_filter:
            self.city = City.objects.filter(slug=self.city_slug_filter).first()

        return super(EventListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['city_filter'] = self.city
        return context

    def get_queryset(self):
        queryset = Event.objects.published().future()

        if self.city:
            queryset = queryset.filter(place__city=self.city)

        return queryset.select_related('place')


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

    def get_queryset(self):
        return Event.objects.published().select_related(
            'place',
        ).prefetch_related(
            'books',
            'speakers',
            'organizers',
        ).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_events'] = Event.objects.exclude(
            id=self.object.id
        ).published().future().select_related('place').order_by('?')[:3]
        context['press_articles'] = \
            get_event_press_articles(self.object).select_related('media_source').distinct()
        context['books'] = \
            list(self.object.books.prefetch_related('authors').published())
        context['organizers'] = list(self.object.organizers.all())
        return context


class OrganizerListView(ListView):
    model = Organizer
    context_object_name = 'organizers'
    paginate_by = 20


class OrganizerDetailView(DetailView):
    model = Organizer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = \
            self.get_object().events.published().future().all()
        context['past_events'] = \
            self.get_object().events.published().past().order_by('-event_date').all()[:18]
        return context


class SpeakerDetailView(DetailView):
    model = Speaker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        speaker = self.get_object()
        context['events'] = speaker.events.published().future().all()
        context['past_events'] = \
            speaker.events.published().past().order_by('-event_date').all()[:9]

        books = []
        if hasattr(speaker, 'book_author'):
            books = list(speaker.book_author.books.prefetch_related('authors').all())
        context['books'] = books

        return context


class SpeakerListView(ListView):
    model = Speaker
    context_object_name = 'speakers'
    paginate_by = 56
    ordering = 'name'

    def dispatch(self, request, *args, **kwargs):
        self.q = request.GET.get('q', '')
        return super(SpeakerListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.q:
            queryset = queryset.filter(name__icontains=self.q)
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
        else:
            return reverse('users:user_added_events_list')

    def form_valid(self, form):
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
        else:
            return reverse('users:user_added_events_list')

    def form_valid(self, form):
        send_notification(self.request, self.object, 'event', False)
        return super().form_valid(form)


class OrganizerCreateView(LoginRequiredMixin, CreateView):
    model = Organizer
    form_class = OrganizerForm

    def form_valid(self, form):
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


class OrganizerAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, item):
        return format_html(
            '<img src="{}" height="20"> {}',
            item.get_image_url(),
            item.name
        )

    def get_selected_result_label(self, item):
        return item.name

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor!
        if not self.request.user.is_authenticated:
            return Organizer.objects.none()

        qs = Organizer.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__unaccent__icontains=self.q)

        return qs


class SpeakerAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, item):
        return format_html(
            '<img src="{}" height="30"> {}',
            item.get_image_url(),
            item.name
        )

    def get_selected_result_label(self, item):
        return item.name

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
                suggestion = mark_safe(
                    'Advertencia para evitar agregar organizadores duplicados: '
                    'ya existe(n) organizador(es) {}.'.format(
                        ', '.join([
                            '<a href="{}">{}</a>'.format(
                                organizer.get_absolute_url(),
                                organizer.name,
                            ) for organizer in organizers
                        ])
                    ),
                )

        return JsonResponse({'suggestion': suggestion})
