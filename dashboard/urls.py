from django.urls import path

from dashboard import views as dashboard_views

app_name = 'dashboard'  # pylint: disable=invalid-name
urlpatterns = [
    path(
        '',
        dashboard_views.HomeView.as_view(),
        name='home',
    ),
    path(
        'social-posts/',
        dashboard_views.SocialPostsListView.as_view(),
        name='social_posts',
    ),
    path(
        'social-posts/source/',
        dashboard_views.social_events_source,
        name='social_posts_source',
    ),
    path(
        'places/',
        dashboard_views.PlacesListView.as_view(),
        name='places',
    ),
    path(
        'users/',
        dashboard_views.UsersView.as_view(),
        name='users',
    ),
    # FILBo
    path(
        'filbo/events/create/',
        dashboard_views.FilboEventFormView.as_view(),
        name='filbo_event_form',
    ),
    # Spreadsheet Sync
    path(
        'spreadsheet-sync/',
        dashboard_views.SpreadsheetSyncFormView.as_view(),
        name='spreadsheet_sync_form',
    ),
]
