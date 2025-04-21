from rest_framework.generics import ListAPIView

from ..models import Event
from .serializers import EventSerializer


class EventListAPIView(ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
