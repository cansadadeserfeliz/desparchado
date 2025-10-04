import logging
from urllib.parse import urlencode

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.cache import cache
from django.db.models import Q
from django.utils.timezone import now
from django.views.generic import ListView

from events.models import Event
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
        """
        Parse search, city, and category query parameters from the request and store them on the view instance; resolve a city slug to a City object and validate the category value.
        
        Parameters:
            request (HttpRequest): Incoming HTTP request whose GET parameters are read.
        
        Returns:
            HttpResponse: Response produced by the superclass dispatch.
        """
        self.search_query_value = request.GET.get(self.search_query_name, '')
        self.city_filter_value = request.GET.get(self.city_filter_name)
        self.category_filter_value = request.GET.get(self.category_filter_name)

        if self.city_filter_value:
            self.city = City.objects.filter(slug=self.city_filter_value).first()

        if self.category_filter_value not in Event.Category:
            self.category_filter_value = ''

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Populate the template context with search and filter metadata plus a URL-encoded pagination query string.
        
        Adds the following keys to the returned context dictionary:
        - `search_query_name`: name of the search query GET parameter.
        - `search_query_value`: current search query value.
        - `city_filter_name`: name of the city filter GET parameter.
        - `city_filter_value`: current city filter value (city slug or empty string).
        - `category_filter_name`: name of the category filter GET parameter.
        - `category_filter_value`: current category filter value (category key or empty string).
        - `category_choices`: available event category choices (from Event.Category.choices).
        - `pagination_query_params`: URL-encoded query string of active search/city/category parameters, prefixed with `&` if any parameters are present, otherwise an empty string.
        
        Returns:
            dict: The view context dictionary, extended with the keys described above.
        """
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
        """
        Builds the queryset of Event objects to display according to the view's filters.
        
        The returned queryset contains published events and, when set on the view instance,
        is filtered by city (place__city) and by category. If the view's search query is at
        or above the configured minimum length, the queryset is further restricted to events
        whose title, description, or speakers' names contain the search text (case-insensitive,
        unaccented) or that match a full-text search on title, description, and speakers' names.
        The final queryset is optimized by selecting the related `place`, prefetching `speakers`,
        ordered by `event_date`, and made distinct to avoid duplicates.
        
        Returns:
            QuerySet: A Django QuerySet of Event objects matching the view's filters and ordering.
        """
        queryset = Event.objects.published()

        if self.city:
            queryset = queryset.filter(place__city=self.city)

        if self.category_filter_value:
            queryset = queryset.filter(category=self.category_filter_value)

        if (
            self.search_query_value
            and len(self.search_query_value) >= self.search_query_min_length
        ):
            queryset = (
                queryset.annotate(
                    search=SearchVector('title', 'description', 'speakers__name'),
                )
                .filter(
                    Q(title__unaccent__icontains=self.search_query_value)
                    | Q(description__unaccent__icontains=self.search_query_value)
                    | Q(speakers__name__unaccent__icontains=self.search_query_value)
                    | Q(search=SearchQuery(self.search_query_value)),
                )
            )

        return (queryset
                .select_related('place')
                .prefetch_related('speakers')
                .order_by('event_date')
                .distinct())


class EventListView(EventListBaseView):
    template_name = 'events/event_list.html'

    def get_queryset(self):
        """
        Return the base queryset restricted to future events.
        
        Returns:
            QuerySet: Event queryset filtered to include only events occurring in the future.
        """
        return super().get_queryset().future()

    def get_context_data(self, **kwargs):
        """
        Add to the template context a queryset of City objects that appear in the current event queryset, using a cached set of city IDs when available.
        
        The method reads city IDs from the cache key 'city_filter_ids' if present; otherwise it derives city IDs from the view's queryset, caches them for 24 hours, and then queries City by those IDs. The resulting queryset is stored in context under the 'cities' key.
        
        Returns:
            context (dict): The template context including a 'cities' entry containing City objects relevant to the current event queryset.
        """
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
        """
        Parse the `year` query parameter, validate and normalize it, and store `year_filter_value` and `year_range` on the view.
        
        Reads the GET parameter named by `year_filter_name`, builds `year_range` as strings from 2017 through the current year, and sets `year_filter_value` to the integer year if it is within `year_range` and convertible to int; otherwise sets `year_filter_value` to None.
        
        Returns:
            The response returned by the superclass `dispatch` call.
        """
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
        """
        Provide a queryset of past events, optionally filtered by the view's year_filter_value, ordered by descending event date.
        
        Returns:
            QuerySet: Event objects that are in the past; if `year_filter_value` is set, only events whose `event_date` year matches that value. Results are ordered by `event_date` in descending order.
        """
        queryset = super().get_queryset().past()

        if self.year_filter_value:
            queryset = queryset.filter(event_date__year=self.year_filter_value)

        return queryset.order_by('-event_date')

    def get_context_data(self, **kwargs):
        """
        Populate the template context with city and year filter metadata and, if a year is selected, append the year parameter to pagination query parameters.
        
        Adds the following keys to the context:
        - "cities": all City objects
        - "year_filter_name": name of the year query parameter
        - "year_filter_value": currently selected year (or None)
        - "year_range": list of valid year strings
        
        If a year is selected, appends an URL-encoded parameter for that year (prefixed with '&') to the existing `pagination_query_params`.
        
        Returns:
            context (dict): The updated context dictionary for the template.
        """
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