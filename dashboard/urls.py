from django.conf.urls import url

from dashboard import views as dashboard_views

urlpatterns = [
    url(
        r'^$',
        dashboard_views.HomeView.as_view(),
        name='home'
    ),
    url(
        r'^events/$',
        dashboard_views.EventsListView.as_view(),
        name='events'
    ),
    url(
        r'^social-posts/$',
        dashboard_views.SocialPostsListView.as_view(),
        name='social_posts'
    ),
    url(
        r'^places/$',
        dashboard_views.PlacesListView.as_view(),
        name='places'
    ),
    url(
        r'^users/$',
        dashboard_views.UsersListView.as_view(),
        name='users'
    ),
    url(
        r'^events-sources/$',
        dashboard_views.EventSourceListView.as_view(),
        name='event_sources'
    ),

    # BLAA
    url(
        r'^blaa/events-list/$',
        dashboard_views.BlaaEventsListView.as_view(),
        name='blaa_events_list'
    ),
    url(
        r'^events/add/$',
        dashboard_views.EventCreateView.as_view(),
        name='event_add'
    ),
]
