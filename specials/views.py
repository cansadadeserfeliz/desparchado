from django.views.generic import DetailView

from .models import Special


class SpecialDetailView(DetailView):
    model = Special
