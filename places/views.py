from django.views.generic import ListView, DetailView, CreateView
from django.utils.html import format_html
from django.core.urlresolvers import reverse

from dal import autocomplete

from .models import Place
from .forms import PlaceForm


class PlaceListView(ListView):
    model = Place
    context_object_name = 'places'
    paginate_by = 9


class PlaceDetailView(DetailView):
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = \
            self.get_object().events.published().future().all()[:9]
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
        if not self.request.user.is_authenticated():
            return Place.objects.none()

        qs = Place.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class PlaceCreateView(CreateView):
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
        return super().form_valid(form)
