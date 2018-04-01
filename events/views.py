from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse

from dal import autocomplete

from .models import Event, Organizer, Speaker
from .forms import EventCreateForm


class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    paginate_by = 9

    def get_queryset(self):
        queryset = Event.objects.published().future()
        return queryset.select_related('place')


class PastEventListView(ListView):
    model = Event
    context_object_name = 'events'
    template_name = 'events/past_event_list.html'
    paginate_by = 9

    def get_queryset(self):
        queryset = Event.objects.published().past().order_by('-event_date')
        return queryset.select_related('place')


class EventDetailView(DetailView):
    model = Event

    def get_queryset(self):
        return Event.objects.published().all()


class OrganizerListView(ListView):
    model = Organizer
    context_object_name = 'organizers'
    paginate_by = 9


class OrganizerDetailView(DetailView):
    model = Organizer


class SpeakerDetailView(DetailView):
    model = Speaker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = \
            self.get_object().events.published().future().all()[:9]
        context['past_events'] = \
            self.get_object().events.published().past().order_by('-event_date').all()[:9]
        return context


class SpeakerListView(ListView):
    model = Speaker
    context_object_name = 'speakers'
    paginate_by = 9


class EventCreateView(LoginRequiredMixin, CreateView):
    form_class = EventCreateForm
    model = Event

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        if self.object.is_published and self.object.is_approved:
            return self.object.get_absolute_url()
        else:
            return reverse('events:event_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_published = True
        self.object.is_approved = True
        self.object.created_by = self.request.user
        self.object.save()
        return super(EventCreateView, self).form_valid(form)


class OrganizerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor!
        if not self.request.user.is_authenticated():
            return Organizer.objects.none()

        qs = Organizer.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
