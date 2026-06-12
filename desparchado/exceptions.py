from django.core.exceptions import PermissionDenied


class UserFacingPermissionDenied(PermissionDenied):
    """PermissionDenied whose message is safe to render directly to end users."""
