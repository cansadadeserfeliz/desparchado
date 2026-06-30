import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView

from desparchado.exceptions import UserFacingPermissionDenied
from events.permissions import QUOTA_EXCEEDED_MESSAGE
from places.models import City

logger = logging.getLogger(__name__)


def get_cities_json():
    cities = City.objects.all().order_by('name')
    cities_data = [{'id': city.id, 'name': city.name} for city in cities]
    return json.dumps(cities_data)


class EventWizardCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'events/event_wizard.html'

    def dispatch(
        self, request: HttpRequest, *args: object, **kwargs: object,
    ) -> HttpResponse:
        # is_authenticated guard is required: this dispatch() runs before
        # LoginRequiredMixin.dispatch() in the MRO, so AnonymousUser has no settings.
        if (
            request.user.is_authenticated
            and request.user.settings.reached_event_creation_quota()
        ):
            logger.warning('Quota reached for user %s', request.user.pk)
            raise UserFacingPermissionDenied(QUOTA_EXCEEDED_MESSAGE)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context['wizard_mode'] = 'create'
        context['api_url'] = reverse('events_api:event_create')

        context['cities_json'] = get_cities_json()

        return context
