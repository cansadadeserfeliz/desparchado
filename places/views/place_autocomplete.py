from desparchado.autocomplete import BaseAutocomplete
from places.models import Place


class PlaceAutocompleteView(BaseAutocomplete):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor!
        """
        Provide a queryset of Place objects for autocomplete suggestions.
        
        Returns Place objects ordered by name when the requesting user is authenticated;
        otherwise returns an empty queryset. If the view has a query string (self.q),
        the results are limited to places whose unaccented names contain the query,
        enabling accent-insensitive, case-insensitive matching for location lookup
        used by events, organizers, and speakers.
        
        Args:
            self: The view instance. Expects attributes `request.user` and `q`.
        
        Returns:
            QuerySet[Place]: A queryset of Place instances matching the access and
            search criteria, ordered by name.
        """
        if not self.request.user.is_authenticated:
            return Place.objects.none()

        qs = Place.objects.order_by('name').all()

        if self.q:
            qs = qs.filter(name__unaccent__icontains=self.q)

        return qs