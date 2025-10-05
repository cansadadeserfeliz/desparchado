import logging

from django.utils.html import format_html

from desparchado.autocomplete import BaseAutocomplete
from events.models import Speaker

logger = logging.getLogger(__name__)


class SpeakerAutocomplete(BaseAutocomplete):

    def get_result_label(self, result):
        return format_html(
            '<img src="{}" height="30"> {}', result.get_image_url(), result.name,
        )

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor!
        if not self.request.user.is_authenticated:
            return Speaker.objects.none()

        qs = Speaker.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__unaccent__icontains=self.q)

        return qs
