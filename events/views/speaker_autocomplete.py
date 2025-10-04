import logging

from django.utils.html import format_html

from desparchado.autocomplete import BaseAutocomplete
from events.models import Speaker

logger = logging.getLogger(__name__)


class SpeakerAutocomplete(BaseAutocomplete):

    def get_result_label(self, result):
        """
        Render an HTML label for a speaker result containing a thumbnail and the speaker's name.
        
        Parameters:
            result (Speaker): Speaker instance; must provide `get_image_url()` and `name` attributes.
        
        Returns:
            str: HTML-safe fragment with the speaker's image (height 30px) followed by the speaker's name.
        """
        return format_html(
            '<img src="{}" height="30"> {}', result.get_image_url(), result.name,
        )

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor!
        """
        Return the queryset of Speaker instances visible to the current request, ordered by name and filtered by the autocomplete query when present.
        
        Returns:
            QuerySet[Speaker]: An empty QuerySet if the requesting user is not authenticated; otherwise a QuerySet of Speaker objects ordered by `name`. If `self.q` is set, the QuerySet is further filtered to speakers whose `name` contains the query, using a case-insensitive, unaccented containment lookup.
        """
        if not self.request.user.is_authenticated:
            return Speaker.objects.none()

        qs = Speaker.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__unaccent__icontains=self.q)

        return qs