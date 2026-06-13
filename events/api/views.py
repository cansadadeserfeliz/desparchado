from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from desparchado.utils import send_notification
from events.serializers.event import EventWriteSerializer

from ..models import Event
from .serializers import EventSerializer


class EventListAPIView(ListAPIView):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['place__city__slug']
    ordering_fields = ['event_date']

    def get_queryset(self):
        return Event.objects.published().order_by('event_date')


class FutureEventListAPIView(EventListAPIView):

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_hidden=False)
        return queryset.future().select_related('place__city')


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
