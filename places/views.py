from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.utils.html import format_html
from django.contrib.auth.mixins import LoginRequiredMixin

from dal import autocomplete

from desparchado.utils import send_notification
from desparchado.mixins import EditorPermissionRequiredMixin
from events.models import Event
from .models import Place
from .models import City
from .forms import PlaceForm


class PlaceListView(ListView):
    model = Place
    context_object_name = 'places'
    paginate_by = 20
    ordering = 'name'


class PlaceDetailView(DetailView):
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = \
            self.get_object().events.published().future().all()
        context['past_events'] = \
            self.get_object().events.published().past().order_by('-event_date').all()[:9]
        return context


class PlaceAutocomplete(autocomplete.Select2QuerySetView):
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
            return Place.objects.none()

        qs = Place.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__unaccent__icontains=self.q)

        return qs


class PlaceCreateView(LoginRequiredMixin, CreateView):
    model = Place
    form_class = PlaceForm

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        return self.object.get_absolute_url()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        send_notification(self.request, self.object, 'place', True)
        return super().form_valid(form)


class PlaceUpdateView(EditorPermissionRequiredMixin, UpdateView):
    model = Place
    form_class = PlaceForm

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        return self.object.get_absolute_url()

    def form_valid(self, form):
        send_notification(self.request, self.object, 'place', False)
        return super().form_valid(form)


class CityDetailView(DetailView):
    model = City

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        events = Event.objects.published().filter(
            place__city=self.object,
        ).future().all()[:9]
        context['events'] = events

        if events.count() <= 3:
            past_events_limit = 9
        else:
            past_events_limit = 3

        context['past_events'] = Event.objects.published().filter(
            place__city=self.object,
        ).past().order_by('-event_date').all()[:past_events_limit]

        return context
