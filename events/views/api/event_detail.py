from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from events.models import Event
from events.serializers.event import EventDetailSerializer
from events.views.api.event_update import EventEditorPermission


# This endpoint exists exclusively to hydrate the edit wizard (EventWizardUpdateView).
# It is NOT a generic event read endpoint — GET is restricted to editors via
# EventEditorPermission intentionally. Do not relax this permission: doing so would
# expose draft event data (organizers, price, source URL, is_published) to any
# authenticated user.
@extend_schema(
    summary='Get event details for editing',
    description='Returns all editable event fields for pre-populating the edit wizard. '
                'Restricted to the event creator, listed editors, and superusers.',
    responses={
        status.HTTP_200_OK: EventDetailSerializer,
        status.HTTP_403_FORBIDDEN: OpenApiResponse(
            description='Not authenticated or not an editor.',
        ),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Event not found.'),
    },
    tags=['events'],
)
class EventDetailAPIView(RetrieveAPIView):
    authentication_classes = [SessionAuthentication]
    serializer_class = EventDetailSerializer
    permission_classes = [IsAuthenticated, EventEditorPermission]
    lookup_field = 'slug'

    def get_queryset(self):
        return Event.objects.select_related('place__city').prefetch_related(
            'organizers',
            'speakers',
        )
