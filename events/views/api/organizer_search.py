from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from events.serializers.organizer import OrganizerSearchSerializer
from events.services.organizer_search import search_organizers


class OrganizerSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        q = request.query_params.get('q', '')
        queryset = search_organizers(q)
        serializer = OrganizerSearchSerializer(queryset, many=True)
        return Response({'results': serializer.data})
