from django.contrib.auth import get_user_model
from django.db.models import Count, DateField
from django.db.models.functions import Cast
from django.views.generic import TemplateView

from dashboard.mixins import SuperuserRequiredMixin
from events.models import Event, Organizer, Speaker
from places.models import Place

User = get_user_model()


class HomeView(SuperuserRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['future_events'] = (Event.objects.published()
                                    .future()
                                    .select_related('place'))
        context['future_events_count'] = Event.objects.published().future().count()

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
        context['active_users_count'] = User.objects.filter(is_active=True).count()
        context['places_count'] = Place.objects.count()
        return context
