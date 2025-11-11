from typing import TypeVar

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Q, QuerySet

from events.models import Event

EventQuerySet = TypeVar("EventQuerySet", bound=QuerySet[Event])


def search_events(
    queryset: EventQuerySet,
    search_str: str,
    search_str_min_length: int = 3,
) -> EventQuerySet:
    """
    Filters an Event queryset by performing a full-text and case-insensitive search.

    The search is applied to the Event's title, description, and related speaker names.
    If the search string is shorter than `search_str_min_length`, the original queryset
    is returned unchanged.

    Args:
        queryset: A Django QuerySet of Event instances.
        search_str: The text string to search for.
        search_str_min_length: Minimum number of characters required to perform
            the search.

    Returns:
        A filtered QuerySet containing Events that match the search criteria.
    """
    if not search_str or len(search_str) < search_str_min_length:
        return queryset

    queryset = queryset.annotate(
        search=SearchVector("title", "description", "speakers__name"),
    ).filter(
        Q(title__unaccent__icontains=search_str)
        | Q(description__unaccent__icontains=search_str)
        | Q(speakers__name__unaccent__icontains=search_str)
        | Q(search=SearchQuery(search_str)),
    )

    # Ensure search results are unique:
    # Including speakers__name in the search vector causes PostgreSQL
    # to emit one row per matching speaker.
    # Without .distinct() the service now returns duplicated Event rows.
    return queryset.distinct()
