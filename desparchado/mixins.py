from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class EditorPermissionRequiredMixin(LoginRequiredMixin):

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if not obj.can_edit(self.request.user):
            raise PermissionDenied()
        return obj
