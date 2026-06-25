from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from events.models import Event
from events.serializers.event import EventWriteSerializer


class EventEditorPermission(BasePermission):
    def has_permission(self, request: Request, view: object) -> bool:
        return True  # IsAuthenticated handles the authentication check

    def has_object_permission(self, request: Request, view: object, obj: Event) -> bool:
        return obj.can_edit(request.user)


@extend_schema(
    summary='Partially update an event',
    description=(
        'Accepts multipart/form-data. All fields are optional (partial update). '
        'Restricted to the event creator, listed editors, and superusers.'
    ),
    request=EventWriteSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            description='Event updated. Returns the event URL.',
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description='Validation errors keyed by field.',
        ),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(
            description='Not authenticated or not an editor.',
        ),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Event not found.'),
    },
    tags=['events'],
)
class EventUpdateAPIView(UpdateAPIView):
    authentication_classes = [SessionAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated, EventEditorPermission]
    serializer_class = EventWriteSerializer
    lookup_field = 'slug'
    http_method_names = ['patch', 'head', 'options']

    def get_queryset(self):
        return Event.objects.select_related('created_by').prefetch_related('editors')

    def update(self, request: Request, *args: object, **kwargs: object) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        return Response({'url': event.get_absolute_url()}, status=status.HTTP_200_OK)
