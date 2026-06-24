from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class EventCreationQuotaPermission(BasePermission):
    message = (
        'Hoy alcanzaste el límite de eventos que puedes crear. '
        'Vuelve mañana para continuar publicando.'
    )

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return not request.user.settings.reached_event_creation_quota()


class OrganizerCreationQuotaPermission(BasePermission):
    message = 'Hoy alcanzaste el límite de nuevos organizadores.'

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return not request.user.settings.reached_organizer_creation_quota()


class SpeakerCreationQuotaPermission(BasePermission):
    message = 'Hoy alcanzaste el límite de nuevos presentadores.'

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return not request.user.settings.reached_speaker_creation_quota()
