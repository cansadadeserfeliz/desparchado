import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView

from desparchado.utils import send_notification
from places.forms import PlaceForm
from places.models import Place

logger = logging.getLogger(__name__)


class PlaceCreateView(LoginRequiredMixin, CreateView):
    model = Place
    form_class = PlaceForm

    def dispatch(self, request, *args, **kwargs):
        """
        Prevent creating a new Place when the current user has reached their place creation quota.
        
        Checks the authenticated user's settings for a reached place-creation quota and, if reached,
        logs a warning and redirects to the user's detail page; otherwise continues normal dispatch.
        
        Args:
            request (HttpRequest): The incoming request used to access the current user.
            *args: Additional positional arguments forwarded to the base dispatch.
            **kwargs: Additional keyword arguments forwarded to the base dispatch.
        
        Returns:
            HttpResponse: A redirect to the user's detail page when the quota is reached,
            or the response returned by the standard dispatch otherwise.
        """
        if request.user.is_authenticated:
            user_settings = request.user.settings
            reached_quota = user_settings.reached_place_creation_quota()

            if reached_quota:
                logger.warning('Quota reached for place creation')
                return HttpResponseRedirect(reverse("users:user_detail"))

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        Return the absolute URL of the created Place instance's detail page.
        
        Returns:
            str: The absolute URL of the created Place instance's detail page.
        """
        return self.object.get_absolute_url()

    def form_valid(self, form):
        # pylint: disable=attribute-defined-outside-init
        """
        Save a new Place instance as created by the current user and send a creation notification.
        
        The method binds the created Place to the requesting user, persists it, triggers a
        notification linking the user and place within the event management context, and then
        continues the standard successful-form handling.
        
        Args:
            form: A valid Django form for creating a Place instance.
        
        Returns:
            HttpResponse: A redirect response to the place's success URL.
        """
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        send_notification(self.request, self.object, 'place', True)
        return super().form_valid(form)