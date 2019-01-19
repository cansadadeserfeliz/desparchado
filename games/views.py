import random

from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import ListView
from django.core.urlresolvers import reverse

from .forms import HuntingOfSnarkGameCreateForm
from .models import HuntingOfSnarkGame
from .models import HuntingOfSnarkCategory
from .models import HuntingOfSnarkCriteria
from .services import get_random_hunting_of_snark_criteria


class HuntingOfSnarkGameCreateView(CreateView):
    form_class = HuntingOfSnarkGameCreateForm
    template_name = 'games/hunting_of_snark_form.html'

    def get_success_url(self):
        return reverse('games:hunting_of_snark_detail', args=(self.object.token,))

    def form_valid(self, form):
        self.object = form.save()
        random_criteria = get_random_hunting_of_snark_criteria(self.object.total_points)
        self.object.criteria.add(*random_criteria)
        if random_criteria.filter(
            public_id=HuntingOfSnarkCriteria.RANDOM_LETTER_CRITERIA_ID
        ).exists():
            self.object.extra = dict(
                random_letter=random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            )
            self.object.save()

        return super().form_valid(form)


class HuntingOfSnarkGameDetailView(DetailView):
    model = HuntingOfSnarkGame
    slug_field = 'token'
    template_name = 'games/hunting_of_snark_detail.html'
    context_object_name = 'game'


class HuntingOfSnarkCriteriaListView(ListView):
    model = HuntingOfSnarkCategory
    template_name = 'games/hunting_of_snark_criteria_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('criteria')
