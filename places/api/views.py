from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from places.serializers.place import PlaceSearchSerializer
from places.services.place_search import search_places


class PlaceSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        q = request.query_params.get('q', '')
        queryset = search_places(q)
        serializer = PlaceSearchSerializer(queryset, many=True)
        return Response({'results': serializer.data})
