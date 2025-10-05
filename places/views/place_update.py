from django.views.generic import UpdateView

from desparchado.mixins import EditorPermissionRequiredMixin
from desparchado.utils import send_notification
from places.forms import PlaceForm
from places.models import Place


class PlaceUpdateView(EditorPermissionRequiredMixin, UpdateView):
    model = Place
    form_class = PlaceForm

    def get_success_url(self):
        """
        Provide the URL to view the updated place.
        
        This redirects users and organizers to the updated Place detail page, where related events
        and speakers associated with that place can be accessed.
        
        Returns:
            str: Absolute URL of the updated Place instance.
        """
        return self.object.get_absolute_url()

    def form_valid(self, form):
        """
        Notify interested parties about the updated place and continue with the standard update flow.
        
        Sends a notification related to the updated Place so connected users (organizers, speakers, or attendees linked to the place)
        are informed, then proceeds with the normal form handling and redirect.
        
        Args:
            form (PlaceForm): Validated form for the Place instance being updated.
        
        Returns:
            HttpResponseRedirect: The response from the superclass form handling (typically a redirect to the place's absolute URL).
        """
        send_notification(self.request, self.object, 'place', False)
        return super().form_valid(form)