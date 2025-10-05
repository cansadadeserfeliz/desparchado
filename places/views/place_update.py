from django.views.generic import UpdateView

from desparchado.mixins import EditorPermissionRequiredMixin
from desparchado.utils import send_notification
from places.forms import PlaceForm
from places.models import Place


class PlaceUpdateView(EditorPermissionRequiredMixin, UpdateView):
    model = Place
    form_class = PlaceForm

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        return self.object.get_absolute_url()

    def form_valid(self, form):
        send_notification(self.request, self.object, 'place', False)
        return super().form_valid(form)
