import logging

from django.urls import reverse
from django.views.generic import UpdateView

from desparchado.mixins import EditorPermissionRequiredMixin
from desparchado.utils import send_notification
from events.forms import EventUpdateForm
from events.models import Event

logger = logging.getLogger(__name__)


class EventUpdateView(EditorPermissionRequiredMixin, UpdateView):
    form_class = EventUpdateForm
    model = Event
    context_object_name = 'event'

    def get_success_url(self):
        if self.object.is_published and self.object.is_approved:
            return self.object.get_absolute_url()

        return reverse('users:user_added_events_list')

    def form_valid(self, form):
        send_notification(self.request, self.object, 'event', False)
        return super().form_valid(form)
