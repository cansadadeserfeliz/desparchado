from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from events.serializers.speaker import SpeakerSearchSerializer
from events.services.speaker_search import search_speakers


class SpeakerSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        q = request.query_params.get('q', '')
        queryset = search_speakers(q)
        serializer = SpeakerSearchSerializer(queryset, many=True)
        return Response({'results': serializer.data})
