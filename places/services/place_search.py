from django.db.models import QuerySet

from places.models import Place


def search_places(q: str, limit: int = 10) -> QuerySet:
    q = q.strip()
    if not q:
        return Place.objects.order_by('name')[:limit]
    if len(q) < 2:
        return Place.objects.none()
    return Place.objects.filter(name__unaccent__icontains=q).order_by('name')[:limit]
