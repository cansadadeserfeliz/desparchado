import logging

from django.views.generic import ListView

from events.models import Organizer

logger = logging.getLogger(__name__)


class OrganizerListView(ListView):
    model = Organizer
    context_object_name = 'organizers'
    paginate_by = 20
