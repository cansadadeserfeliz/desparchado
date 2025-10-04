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
        """
        Capture the 'q' GET parameter into the view instance and continue normal dispatch.
        
        Reads the 'q' parameter from request.GET (defaults to an empty string) and assigns it to self.q, then delegates to the superclass dispatch method.
        
        Parameters:
            request: HttpRequest object for the current request.
        
        Returns:
            The response returned by the superclass dispatch.
        """
        self.q = request.GET.get('q', '')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return the view's queryset, optionally filtered by the view's search query.
        
        If the view's `q` attribute is non-empty, the queryset is restricted to objects whose `name`
        or unaccented `name` contains `q` (case-insensitive).
        
        Returns:
            QuerySet: The resulting queryset of Speaker objects.
        """
        queryset = super().get_queryset()
        if self.q:
            queryset = queryset.annotate(
                unaccent_name=SearchVector('name__unaccent'),
            ).filter(Q(name__icontains=self.q) | Q(unaccent_name__icontains=self.q))
        return queryset

    def get_context_data(self, **kwargs):
        """
        Add the current search query to the template context.
        
        Parameters:
            **kwargs: Additional keyword arguments passed to the parent context builder.
        
        Returns:
            context (dict): The template context with 'search_string' set to the view's current query.
        """
        context = super().get_context_data(**kwargs)
        context['search_string'] = self.q
        return context