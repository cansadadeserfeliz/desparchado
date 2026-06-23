from django.db.models import QuerySet

from events.models import Organizer


def search_organizers(q: str, limit: int = 10) -> QuerySet:
    """Search organizers by name using accent-insensitive substring matching.

    Args:
        q: Search query string. Empty string returns the first `limit` records.
            Single-character queries return no results. Two or more characters
            trigger a filtered search using ``unaccent__icontains``.
        limit: Maximum number of results to return.

    Returns:
        A QuerySet of Organizer instances ordered by name.
    """
    q = q.strip()
    if not q:
        return Organizer.objects.order_by('name')[:limit]
    if len(q) < 2:
        return Organizer.objects.none()
    return (
        Organizer.objects.filter(name__unaccent__icontains=q).order_by('name')[:limit]
    )
