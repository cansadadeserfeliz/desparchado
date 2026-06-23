from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from events.models import Event
from events.serializers.event import EventListSerializer

_event_list_params = [
    OpenApiParameter(
        'place__city__slug',
        str,
        description='Filter events by city slug.',
    ),
    OpenApiParameter(
        'ordering',
        str,
        description='Order results. Allowed: `event_date`, `-event_date`.',
    ),
]


@extend_schema(
    summary='List published events',
    parameters=_event_list_params,
    tags=['events'],
)
class EventListAPIView(ListAPIView):
    serializer_class = EventListSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['place__city__slug']
    ordering_fields = ['event_date']

    def get_queryset(self):
        return Event.objects.published().order_by('event_date')


@extend_schema(
    summary='List upcoming published events',
    parameters=_event_list_params,
    tags=['events'],
)
class FutureEventListAPIView(EventListAPIView):

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_hidden=False)
        return queryset.future().select_related('place__city')
