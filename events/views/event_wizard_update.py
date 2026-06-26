import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView

from desparchado.exceptions import UserFacingPermissionDenied
from events.models import Event

logger = logging.getLogger(__name__)

EDIT_DENIED_MESSAGE = 'No tienes permiso para editar este evento.'


class EventWizardUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'events/event_wizard.html'

    def dispatch(
        self, request: HttpRequest, *args: object, **kwargs: object,
    ) -> HttpResponse:
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        try:
            self.object = Event.objects.get(slug=kwargs['slug'])
        except Event.DoesNotExist:
            raise Http404 from None
        if not self.object.can_edit(request.user):
            logger.warning(
                'Edit permission denied for user %s on event %s',
                request.user.pk,
                self.object.pk,
            )
            raise UserFacingPermissionDenied(EDIT_DENIED_MESSAGE)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context['wizard_mode'] = 'edit'
        context['api_url'] = reverse('events_api:event_detail', args=[self.object.slug])
        context['api_update_url'] = reverse(
            'events_api:event_update', args=[self.object.slug],
        )
        return context
