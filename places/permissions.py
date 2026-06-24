from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class PlaceCreationQuotaPermission(BasePermission):
    message = 'Hoy alcanzaste el límite de nuevos lugares.'

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return not request.user.settings.reached_place_creation_quota()
