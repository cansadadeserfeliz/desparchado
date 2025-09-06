from django.views.generic import ListView

from dashboard.mixins import SuperuserRequiredMixin
from places.models import Place


class PlacesListView(SuperuserRequiredMixin, ListView):
    model = Place
    paginate_by = 300
    context_object_name = 'places'
    template_name = 'dashboard/places.html'
