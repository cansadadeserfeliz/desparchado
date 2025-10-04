import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView

from desparchado.utils import send_notification
from events.forms import OrganizerForm
from events.models import Organizer

logger = logging.getLogger(__name__)


class OrganizerCreateView(LoginRequiredMixin, CreateView):
    model = Organizer
    form_class = OrganizerForm

    def dispatch(self, request, *args, **kwargs):
        """
        Enforce the user's organizer creation quota and redirect to
        the user's detail page if the quota is reached.

        Returns:
            HttpResponse: A redirect to the user's detail page when the quota is reached
            or the standard dispatch response otherwise.
        """
        if request.user.is_authenticated:
            user_settings = request.user.settings
            reached_quota = user_settings.reached_organizer_creation_quota()

            if reached_quota:
                logger.warning('Quota reached for organizer creation')
                return HttpResponseRedirect(reverse("users:user_detail"))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # pylint: disable=attribute-defined-outside-init
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()

        send_notification(self.request, self.object, 'organizer', True)
        return super().form_valid(form)
