from django.db.models import QuerySet

from events.models import Speaker


def search_speakers(q: str, limit: int = 10) -> QuerySet:
    """Search speakers by name using accent-insensitive substring matching.

    Args:
        q: Search query string. Empty string returns the first `limit` records.
            Single-character queries return no results. Two or more characters
            trigger a filtered search using ``unaccent__icontains``.
        limit: Maximum number of results to return.

    Returns:
        A QuerySet of Speaker instances ordered by name.
    """
    q = q.strip()
    if not q:
        return Speaker.objects.order_by('name')[:limit]
    if len(q) < 2:
        return Speaker.objects.none()
    return Speaker.objects.filter(name__unaccent__icontains=q).order_by('name')[:limit]
