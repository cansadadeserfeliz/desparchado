from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from django.views.generic import TemplateView

from dashboard.mixins import SuperuserRequiredMixin

User = get_user_model()


class UsersView(SuperuserRequiredMixin, TemplateView):
    template_name = "dashboard/users.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        users_with_most_events = User.objects.annotate(
            event_count=Count("created_events"),
        ).filter(event_count__gt=0).order_by("-event_count")[:20]
        context['users_with_most_events'] = users_with_most_events

        recently_registered_users = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=90),
        )
        context['recently_registered_users'] = recently_registered_users

        duplicated_emails = (
            User.objects.values("email")
            .annotate(email_count=Count("id"))
            .filter(email_count__gt=1)
        )
        context['duplicated_emails'] = duplicated_emails
        return context
