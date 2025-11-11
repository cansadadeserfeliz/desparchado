import logging
from urllib.parse import urlencode

from django.core.cache import cache
from django.utils.timezone import now
from django.views.generic import ListView

from events.models import Event
from events.services import search_events
from places.models import City

logger = logging.getLogger(__name__)


class EventListBaseView(ListView):
    model = Event
    context_object_name = 'events'
    paginate_by = 15
    search_query_name = 'q'
    search_query_value = ''
    search_query_min_length = 3
    city_filter_name = 'city'
    city_filter_value = ''
    city = None
    category_filter_name = 'category'
    category_filter_value = ''

    def dispatch(self, request, *args, **kwargs):
        self.search_query_value = request.GET.get(self.search_query_name, '')
        self.city_filter_value = request.GET.get(self.city_filter_name)
        self.category_filter_value = request.GET.get(self.category_filter_name)

        if self.city_filter_value:
            self.city = City.objects.filter(slug=self.city_filter_value).first()

        if self.category_filter_value not in Event.Category:
            self.category_filter_value = ''

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # For search form rendering
        context['search_query_name'] = self.search_query_name
        context['search_query_value'] = self.search_query_value
        context['city_filter_name'] = self.city_filter_name
        context['city_filter_value'] = self.city_filter_value
        context['category_filter_name'] = self.category_filter_name
        context['category_filter_value'] = self.category_filter_value
        context['category_choices'] = Event.Category.choices

        params = {}
        if self.search_query_value:
            params[self.search_query_name] = self.search_query_value
        if self.city_filter_value:
            params[self.city_filter_name] = self.city_filter_value
        if self.category_filter_value:
            params[self.category_filter_name] = self.category_filter_value
        context['pagination_query_params'] = f"&{urlencode(params)}" if params else ''

        return context

    def get_queryset(self):
        queryset = Event.objects.published()

        if self.city:
            queryset = queryset.filter(place__city=self.city)

        if self.category_filter_value:
            queryset = queryset.filter(category=self.category_filter_value)

        queryset = search_events(
            queryset=queryset,
            search_str=self.search_query_value,
            search_str_min_length=self.search_query_min_length,
        )

        return (queryset
                .select_related('place')
                .prefetch_related('speakers')
                .order_by('event_date')
                .distinct())


class EventListView(EventListBaseView):
    template_name = 'events/event_list.html'

    def get_queryset(self):
        return super().get_queryset().future()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'city_filter_ids' in cache:
            city_ids = cache.get('city_filter_ids')
        else:
            events = self.get_queryset()
            city_ids = events.values_list("place__city_id", flat=True)
            cache.set('city_filter_ids', city_ids, 24 * 60 * 60)

        context['cities'] = City.objects.filter(id__in=city_ids)

        return context


class PastEventListView(EventListBaseView):
    template_name = "events/past_event_list.html"
    year_filter_name = 'year'
    year_filter_value = None
    year_range = []

    def dispatch(self, request, *args, **kwargs):
        self.year_filter_value = request.GET.get(self.year_filter_name, None)
        self.year_range = list(map(str, range(2017, now().year + 1)))

        if self.year_filter_value not in self.year_range:
            self.year_filter_value = None
        try:
            self.year_filter_value = int(self.year_filter_value)
        except (ValueError, TypeError):
            self.year_filter_value = None

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().past()

        if self.year_filter_value:
            queryset = queryset.filter(event_date__year=self.year_filter_value)

        return queryset.order_by('-event_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # For search form rendering
        context["cities"] = City.objects.all()
        context['year_filter_name'] = self.year_filter_name
        context['year_filter_value'] = self.year_filter_value
        context['year_range'] = self.year_range

        if self.year_filter_value:
            params = {self.year_filter_name: self.year_filter_value}
            context['pagination_query_params'] += f"&{urlencode(params)}"

        return context
