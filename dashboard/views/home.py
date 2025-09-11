from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, DateField
from django.db.models.functions import Cast
from django.views.generic import TemplateView
from django.utils import timezone

from dashboard.mixins import SuperuserRequiredMixin
from events.models import Event, Organizer, Speaker
from places.models import Place

User = get_user_model()


class HomeView(SuperuserRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        future_qs = Event.objects.published().future()
        context["future_events"] = future_qs.select_related("place")
        context["future_events_count"] = future_qs.count()

        context['future_events_by_date'] = (
            Event.objects.published()
            .future()
            .annotate(day=Cast('event_date', DateField()))
            .values('day')
            .annotate(count=Count('day'))
            .values('day', 'count')
            .order_by('day')
        )
        context['organizers_count'] = Organizer.objects.count()
        context['speakers_count'] = Speaker.objects.count()
        context['speakers_without_image_count'] = Speaker.objects.filter(
            image='',
        ).count()
        context['active_users_count'] = User.objects.filter(
            is_active=True,
            last_login__gt=timezone.now() - timedelta(days=60),
        ).count()
        context['places_count'] = Place.objects.count()
        return context
