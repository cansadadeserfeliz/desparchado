import logging

from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic import TemplateView

from desparchado.exceptions import UserFacingPermissionDenied
from desparchado.mixins import EditorPermissionRequiredMixin
from events.models import Event

logger = logging.getLogger(__name__)

EDIT_DENIED_MESSAGE = 'No tienes permiso para editar este evento.'


class EventWizardUpdateView(EditorPermissionRequiredMixin, TemplateView):
    template_name = 'events/event_wizard.html'

    def dispatch(
        self, request: HttpRequest, *args: object, **kwargs: object,
    ) -> HttpResponse:
        if request.user.is_authenticated:
            try:
                self.object = Event.objects.get(slug=kwargs['slug'])
            except Event.DoesNotExist:
                raise Http404
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
        context['api_url'] = f'/events/api/v1/events/{self.object.slug}/'
        return context
