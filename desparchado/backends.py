import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

logger = logging.getLogger(__name__)


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        # Accept `email` alias and validate inputs early
        username = kwargs.get("email", username)
        if username is None or password is None:
            return None

        # Normalize and case-insensitive email lookup; avoid MultipleObjectsReturned
        try:
            normalized = (
                UserModel.objects.normalize_email(username)
                if hasattr(UserModel.objects, "normalize_email")
                else username
            )
            users = UserModel.objects.filter(email__iexact=normalized)

            if users.count() > 1:
                logger.error(f"Multiple users found for email {username}")

            user = users.first()
        except Exception:
            user = None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
