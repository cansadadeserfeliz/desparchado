from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from desparchado.utils import send_notification
from events.serializers.event import EventWriteSerializer


@extend_schema(
    summary='Create a new event',
    request=EventWriteSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            description='Event created. Returns the new event URL.',
        ),
    },
    tags=['events'],
)
class EventCreateAPIView(CreateAPIView):
    serializer_class = EventWriteSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: EventWriteSerializer) -> None:
        event = serializer.save(
            created_by=self.request.user,
            is_approved=True,
        )
        send_notification(self.request, event, 'event', True)

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                'url': serializer.instance.get_absolute_url(),
            },
            status=status.HTTP_201_CREATED,
        )
