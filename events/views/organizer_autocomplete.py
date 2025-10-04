import logging

from desparchado.autocomplete import BaseAutocomplete
from events.models import Organizer

logger = logging.getLogger(__name__)


class OrganizerAutocompleteView(BaseAutocomplete):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor!
        """
        Return a queryset of Organizer instances appropriate for the current request and query.
        
        If the request's user is not authenticated, returns an empty queryset. Otherwise returns Organizers ordered by name; if `self.q` is set, the queryset is further filtered to organizers whose name contains `self.q`, using case-insensitive, unaccent-insensitive matching.
        
        Returns:
            QuerySet: A Django QuerySet of Organizer objects matching the authentication and search criteria.
        """
        if not self.request.user.is_authenticated:
            return Organizer.objects.none()

        qs = Organizer.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__unaccent__icontains=self.q)

        return qs