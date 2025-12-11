import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.views import View

from events.models import Organizer

logger = logging.getLogger(__name__)


class OrganizerSuggestionsView(LoginRequiredMixin, View):

    def get(self, request):
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
