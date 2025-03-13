from django.urls import path

from dashboard import views as dashboard_views

app_name = 'dashboard'
urlpatterns = [
    path(
        '',
        dashboard_views.HomeView.as_view(),
        name='home'
    ),
    path(
        'social-posts/',
        dashboard_views.SocialPostsListView.as_view(),
        name='social_posts'
    ),
    path(
        'social-posts/source/',
        dashboard_views.social_events_source,
        name='social_posts_source'
    ),
    path(
        'places/',
        dashboard_views.PlacesListView.as_view(),
        name='places'
    ),
    path(
        'users/',
        dashboard_views.UsersListView.as_view(),
        name='users'
    ),

    # BLAA
    path(
        'blaa/events-list/',
        dashboard_views.BlaaEventsListView.as_view(),
        name='blaa_events_list'
    ),
    path(
        'events/add/',
        dashboard_views.EventCreateView.as_view(),
        name='event_add'
    ),
]
