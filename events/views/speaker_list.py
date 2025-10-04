import logging

from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django.views.generic import ListView

from events.models import Speaker

logger = logging.getLogger(__name__)


class SpeakerListView(ListView):
    model = Speaker
    context_object_name = 'speakers'
    paginate_by = 54
    ordering = 'name'
    q = ''

    def dispatch(self, request, *args, **kwargs):
        self.q = request.GET.get('q', '')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.q:
            queryset = queryset.annotate(
                unaccent_name=SearchVector('name__unaccent'),
            ).filter(Q(name__icontains=self.q) | Q(unaccent_name__icontains=self.q))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_string'] = self.q
        return context
