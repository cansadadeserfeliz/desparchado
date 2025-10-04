import logging

from django.views.generic import UpdateView

from desparchado.mixins import EditorPermissionRequiredMixin
from desparchado.utils import send_notification
from events.forms import SpeakerForm
from events.models import Speaker

logger = logging.getLogger(__name__)


class SpeakerUpdateView(EditorPermissionRequiredMixin, UpdateView):
    model = Speaker
    form_class = SpeakerForm

    def form_valid(self, form):
        """
        Handle a valid form submission for updating a speaker.
        
        Sends a notification about the updated speaker and then continues with the normal success handling provided by the base view.
        
        Returns:
            HttpResponse: The response produced by the base class's success handling (typically a redirect to the success or detail page).
        """
        send_notification(self.request, self.object, 'speaker', False)
        return super().form_valid(form)