import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView

from desparchado.utils import send_notification
from events.forms import SpeakerForm
from events.models import Speaker

logger = logging.getLogger(__name__)


class SpeakerCreateView(LoginRequiredMixin, CreateView):
    model = Speaker
    form_class = SpeakerForm

    def dispatch(self, request, *args, **kwargs):
        """
        Check the user's speaker creation quota and redirect to the user's detail page if the quota is reached.
        
        Returns:
            HttpResponse: A redirect to the users:user_detail URL when the quota is reached, or the superclass dispatch response otherwise.
        """
        if request.user.is_authenticated:
            user_settings = request.user.settings
            reached_quota = user_settings.reached_speaker_creation_quota()

            if reached_quota:
                logger.warning('Quota reached for speaker creation')
                return HttpResponseRedirect(reverse("users:user_detail"))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # pylint: disable=attribute-defined-outside-init
        """
        Handle a valid speaker form by saving the speaker, recording its creator, and sending a notification before continuing the standard success flow.
        
        Saves the form instance with the current user set as `created_by`, sends a `'speaker'` notification for the created object, and then delegates to the superclass to produce the final response.
        
        Returns:
            HttpResponse: The response produced by the standard `form_valid` handling (typically a redirect to the created object's page).
        """
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()

        send_notification(self.request, self.object, 'speaker', True)
        return super().form_valid(form)