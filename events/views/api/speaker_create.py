from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from events.permissions import SpeakerCreationQuotaPermission
from events.serializers.speaker import SpeakerCreateSerializer


@extend_schema(
    summary='Create a new speaker',
    request=SpeakerCreateSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            description='Speaker created. Returns id and name.',
        ),
    },
    tags=['events'],
)
class SpeakerCreateAPIView(CreateAPIView):
    serializer_class = SpeakerCreateSerializer
    permission_classes = [IsAuthenticated, SpeakerCreationQuotaPermission]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer: SpeakerCreateSerializer) -> None:
        serializer.save(created_by=self.request.user)

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'id': serializer.instance.pk, 'name': serializer.instance.name},
            status=status.HTTP_201_CREATED,
        )
