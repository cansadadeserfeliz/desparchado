from dateutil.parser import parse
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from dashboard.mixins import SuperuserRequiredMixin
from events.models import Event, SocialNetworkPost


class SocialPostsListView(SuperuserRequiredMixin, TemplateView):
    template_name = 'dashboard/social_posts.html'


def social_events_source(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'You are not authorized'})

    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    event_list = []

    start_date = parse(start_date)
    end_date = parse(end_date)

    blue = '#0073b7'
    green = '#00a65a'
    muted = '#777777'

    events = (
        Event.objects.published()
        .filter(
            event_date__date__range=(start_date, end_date),
        )
        .prefetch_related('social_posts')
        .order_by('event_date')
        .all()
    )
    for event in events:
        if event.social_posts.exists():
            color = green
        else:
            color = muted
        local_date = timezone.localtime(event.event_date)
        event_list.append(
            {
                'title': event.title,
                'start': local_date.isoformat(),
                'backgroundColor': color,
                'borderColor': color,
                'url': reverse('admin:events_event_change', args=(event.id,)),
                'extendedProps': {'imageUrl': event.get_image_url()},
            },
        )

    social_posts = (
        SocialNetworkPost.objects.filter(
            published_at__range=(start_date, end_date),
        )
        .select_related('event', 'created_by')
        .all()
    )

    for social_post in social_posts:
        local_date = timezone.localtime(social_post.published_at)
        event_list.append(
            {
                'title': social_post.event.title,
                'start': local_date.isoformat(),
                'backgroundColor': blue,
                'borderColor': blue,
                'url': reverse(
                    'admin:events_event_change', args=(social_post.event.id,),
                ),
                'extendedProps': {'imageUrl': social_post.event.get_image_url()},
            },
        )

    return JsonResponse(event_list, safe=False)
