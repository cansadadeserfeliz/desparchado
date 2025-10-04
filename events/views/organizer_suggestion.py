import logging

from django.http import JsonResponse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.views import View

from events.models import Organizer

logger = logging.getLogger(__name__)


class OrganizerSuggestionsView(View):
    def get(self, request):
        """
        Provide organizer name suggestions based on the 'query' GET parameter.
        
        Checks the request's 'query' parameter; if it has at least 5 characters, searches for up to three organizers whose names match the query (case-insensitive, unaccented). If matches are found, returns a JSON response containing an HTML-safe suggestion message with links to the matching organizers; otherwise the suggestion is null.
        
        Parameters:
            request: Django HttpRequest from which the 'query' GET parameter is read.
        
        Returns:
            JsonResponse: A JSON object with a single key `suggestion` whose value is an HTML string with linked organizer names when duplicates are found, or `None` when no suggestion is available.
        """
        query = request.GET.get('query', '')
        suggestion = None
        if len(query) >= 5:
            organizers = Organizer.objects.filter(
                name__unaccent__icontains=query,
            )[:3]
            if organizers:
                duplicated_organizers = ', '.join(
                    [
                        f'<a href="{organizer.get_absolute_url()}">'
                        f'{escape(organizer.name)}</a>'
                        for organizer in organizers
                    ],
                )

                suggestion = mark_safe(  # noqa: S308
                    'Advertencia para evitar agregar organizadores duplicados: '
                    f'ya existe(n) organizador(es) {duplicated_organizers}.',
                )

        return JsonResponse({'suggestion': suggestion})