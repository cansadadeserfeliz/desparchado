from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from dal import autocomplete

from desparchado.utils import send_notification
from .models import Event, Organizer, Speaker
from .forms import EventCreateForm
from .forms import OrganizerForm
from .forms import SpeakerForm


class EventListView(ListView):
    model = Event
    context_object_name = 'events'
    paginate_by = 27

    def get_queryset(self):
        queryset = Event.objects.published().future()
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
        return Event.objects.published().all()


class OrganizerListView(ListView):
    model = Organizer
    context_object_name = 'organizers'
    paginate_by = 20


class OrganizerDetailView(DetailView):
    model = Organizer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = \
            self.get_object().events.published().future().all()[:9]
        context['past_events'] = \
            self.get_object().events.published().past().order_by('-event_date').all()[:9]
        return context


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
    paginate_by = 20
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


class EventUpdateView(LoginRequiredMixin, UpdateView):
    form_class = EventCreateForm
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


class OrganizerCreateView(CreateView):
    model = Organizer
    form_class = OrganizerForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()

        send_notification(self.request, self.object, 'organizer', True)
        return super().form_valid(form)


class OrganizerUpdateView(UpdateView):
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


class SpeakerUpdateView(LoginRequiredMixin, UpdateView):
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
        if not self.request.user.is_authenticated():
            return Organizer.objects.none()

        qs = Organizer.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

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
        if not self.request.user.is_authenticated():
            return Speaker.objects.none()

        qs = Speaker.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
