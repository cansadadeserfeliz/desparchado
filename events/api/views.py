from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from ..models import Event
from .serializers import EventCreateSerializer, EventSerializer


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
    serializer_class = EventCreateSerializer
    permission_classes = [IsAuthenticated]
