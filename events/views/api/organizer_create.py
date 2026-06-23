from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from events.serializers.organizer import OrganizerCreateSerializer


@extend_schema(
    summary='Create a new organizer',
    request=OrganizerCreateSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            description='Organizer created. Returns id and name.',
        ),
    },
    tags=['events'],
)
class OrganizerCreateAPIView(CreateAPIView):
    serializer_class = OrganizerCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer: OrganizerCreateSerializer) -> None:
        serializer.save(created_by=self.request.user)

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'id': serializer.instance.pk, 'name': serializer.instance.name},
            status=status.HTTP_201_CREATED,
        )
