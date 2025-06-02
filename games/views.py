import random

from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from .forms import HuntingOfSnarkGameCreateForm
from .models import HuntingOfSnarkCategory, HuntingOfSnarkCriteria, HuntingOfSnarkGame
from .services import get_random_hunting_of_snark_criteria


class HuntingOfSnarkGameCreateView(CreateView):
    form_class = HuntingOfSnarkGameCreateForm
    template_name = 'games/hunting_of_snark_form.html'

    def get_success_url(self):
        return reverse('games:hunting_of_snark_detail', args=(self.object.token,))

    def form_valid(self, form):
        self.object = form.save()  # pylint: disable=attribute-defined-outside-init
        random_criteria = get_random_hunting_of_snark_criteria(self.object.total_points)
        self.object.criteria.add(*random_criteria)
        if random_criteria.filter(
            public_id=HuntingOfSnarkCriteria.RANDOM_LETTER_CRITERIA_ID,
        ).exists():
            self.object.extra = {
                "random_letter": random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
            }
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


class HuntingOfSnarkGameListView(ListView):
    model = HuntingOfSnarkGame
    template_name = 'games/hunting_of_snark_game_list.html'
    context_object_name = 'games'
    paginate_by = 100
    q = ''

    def dispatch(self, request, *args, **kwargs):
        self.q = request.GET.get('q', '')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.q:
            queryset = queryset.filter(player_name__icontains=self.q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_string'] = self.q
        return context
