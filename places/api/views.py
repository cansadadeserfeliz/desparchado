from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from places.serializers.place import PlaceCreateSerializer, PlaceSearchSerializer
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


@extend_schema(
    summary='Create a new place',
    request=PlaceCreateSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            description='Place created. Returns id and name.',
        ),
    },
    tags=['places'],
)
class PlaceCreateAPIView(CreateAPIView):
    serializer_class = PlaceCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer: PlaceCreateSerializer) -> None:
        serializer.save(created_by=self.request.user)

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'id': serializer.instance.pk, 'name': serializer.instance.name},
            status=status.HTTP_201_CREATED,
        )
