import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from desparchado.autocomplete import BaseAutocomplete
from desparchado.mixins import EditorPermissionRequiredMixin
from desparchado.utils import send_notification
from events.models import Event

from .forms import PlaceForm
from .models import City, Place

logger = logging.getLogger(__name__)


class PlaceListView(ListView):
    model = Place
    context_object_name = 'places'
    paginate_by = 20
    ordering = 'name'


class PlaceDetailView(DetailView):
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["events"] = (
            self.get_object()
            .events.published()
            .future()
            .select_related("place")
            .prefetch_related("speakers")
            .all()[:15]
        )
        context["past_events"] = (
            self.get_object()
            .events.published()
            .past()
            .order_by("-event_date")
            .select_related("place")
            .prefetch_related("speakers")
            .all()[:9]
        )
        return context


class PlaceAutocomplete(BaseAutocomplete):

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

    def dispatch(self, request, *args, **kwargs):
        """
        Check place creation quota before showing the form.
        If exceeded, redirect to user profile page that will show an error message.
        """
        if request.user.is_authenticated:
            user_settings = request.user.settings
            reached_quota = user_settings.reached_place_creation_quota()

            if reached_quota:
                logger.warning('Quota reached for place creation')
                return HttpResponseRedirect(reverse("users:user_detail"))

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        return self.object.get_absolute_url()

    def form_valid(self, form):
        # pylint: disable=attribute-defined-outside-init
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

        events = (
            Event.objects.published()
            .filter(
                place__city=self.object,
            )
            .future()
            .select_related("place")
            .all()[:9]
        )
        context['events'] = events

        if events.count() <= 3:
            past_events_limit = 9
        else:
            past_events_limit = 3

        context["past_events"] = (
            Event.objects.published()
            .filter(
                place__city=self.object,
            )
            .past()
            .order_by("-event_date")
            .select_related("place")
            .all()[:past_events_limit]
        )

        return context
