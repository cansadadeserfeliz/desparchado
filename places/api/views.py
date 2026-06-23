from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from places.serializers.place import PlaceSearchSerializer
from places.services.place_search import search_places


class PlaceSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Search places by name',
        parameters=[
            OpenApiParameter('q', str, description='Search query (min 3 chars)'),
        ],
        responses={
            status.HTTP_200_OK: inline_serializer(
                'PlaceSearchResponse',
                fields={'results': PlaceSearchSerializer(many=True)},
            ),
        },
        tags=['places'],
    )
    def get(self, request: Request) -> Response:
        q = request.query_params.get('q', '')
        queryset = search_places(q)
        serializer = PlaceSearchSerializer(queryset, many=True)
        return Response({'results': serializer.data})
