from rest_framework.generics import ListAPIView

from ..models import Event
from .serializers import EventSerializer


class EventListAPIView(ListAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.published().order_by('event_date')


class FutureEventListAPIView(EventListAPIView):

    def get_queryset(self):
        queryset = super(FutureEventListAPIView, self).get_queryset()
        return queryset.future()
