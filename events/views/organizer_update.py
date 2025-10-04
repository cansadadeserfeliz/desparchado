import logging

from django.views.generic import UpdateView

from desparchado.mixins import EditorPermissionRequiredMixin
from desparchado.utils import send_notification
from events.forms import OrganizerForm
from events.models import Organizer

logger = logging.getLogger(__name__)


class OrganizerUpdateView(EditorPermissionRequiredMixin, UpdateView):
    model = Organizer
    form_class = OrganizerForm

    def form_valid(self, form):
        """
        Handle a valid form submission by sending a notification about the updated organizer and continuing standard successful form processing.
        
        Parameters:
            form (forms.Form): Valid form instance for the Organizer being updated.
        
        Returns:
            HttpResponse: The response produced by the standard successful form handler (typically a redirect).
        """
        send_notification(self.request, self.object, 'organizer', False)
        return super().form_valid(form)