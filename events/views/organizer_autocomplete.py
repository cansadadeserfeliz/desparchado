import logging

from desparchado.autocomplete import BaseAutocomplete
from events.models import Organizer

logger = logging.getLogger(__name__)


class OrganizerAutocompleteView(BaseAutocomplete):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor!
        if not self.request.user.is_authenticated:
            return Organizer.objects.none()

        qs = Organizer.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__unaccent__icontains=self.q)

        return qs
