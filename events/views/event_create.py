import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView

from desparchado.utils import send_notification
from events.forms import EventCreateForm
from events.models import Event

logger = logging.getLogger(__name__)


class EventCreateView(LoginRequiredMixin, CreateView):
    form_class = EventCreateForm
    model = Event

    def dispatch(self, request, *args, **kwargs):
        """
        Enforce the user's event creation quota and redirect to
        the user's detail page if the quota is reached.

        Returns:
            HttpResponse: A redirect to the user's detail page when the quota is reached
            or the standard dispatch response otherwise.
        """
        if request.user.is_authenticated:
            user_settings = request.user.settings
            reached_quota = user_settings.reached_event_creation_quota()

            if reached_quota:
                logger.warning('Quota reached for event creation')
                return HttpResponseRedirect(reverse("users:user_detail"))

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.is_published and self.object.is_approved:
            return self.object.get_absolute_url()

        return reverse('users:user_added_events_list')

    def form_valid(self, form):
        # pylint: disable=attribute-defined-outside-init
        self.object = form.save(commit=False)
        self.object.is_approved = True
        self.object.created_by = self.request.user
        self.object.save()

        send_notification(self.request, self.object, 'event', True)
        return super().form_valid(form)
