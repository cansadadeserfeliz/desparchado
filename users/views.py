from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import DetailView, ListView

from events.models import Event

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'user_obj'
    model = User
    template_name = 'auth/user_detail.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        """Extend the template context."""
        context = super().get_context_data(**kwargs)

        added_events_count = (
            Event.objects.filter(created_by=self.object).published().count()
        )
        context["added_events_count"] = added_events_count

        creation_quota_error_message = None
        quota_reached_model_names = []

        user_settings = self.object.settings
        if user_settings.reached_event_creation_quota():
            quota_reached_model_names.append(_("eventos"))
        if user_settings.reached_place_creation_quota():
            quota_reached_model_names.append(_("lugares"))
        if user_settings.reached_organizer_creation_quota():
            quota_reached_model_names.append(_("organizadores"))
        if user_settings.reached_speaker_creation_quota():
            quota_reached_model_names.append(_("presentadores"))

        if quota_reached_model_names:
            creation_quota_error_message = _("Has alcanzado tu cuota de creación de ")
            creation_quota_error_message += ", ".join(quota_reached_model_names)
            creation_quota_error_message += "."

        context["creation_quota_error_message"] = creation_quota_error_message

        days_on_page = (timezone.now() - self.object.date_joined).days
        context['days_on_page'] = days_on_page

        return context


class UserAddedEventsListView(LoginRequiredMixin, ListView):
    model = Event
    paginate_by = 30
    template_name = 'auth/user_added_events_list.html'
    context_object_name = 'events'
    ordering = 'modified'

    def get_queryset(self):
        return Event.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_object'] = self.request.user
        return context
