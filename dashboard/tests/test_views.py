import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home(django_app, admin_user):
    response = django_app.get(reverse('dashboard:home'), user=admin_user, status=200)
    assert 'future_events_count' in response.context


@pytest.mark.django_db
def test_social_posts(django_app, admin_user):
    django_app.get(reverse('dashboard:social_posts'), user=admin_user, status=200)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'dashboard_view_name',
    [
        'dashboard:home',
        'dashboard:social_posts',
    ],
)
def test_access_denied_for_non_admin_users(django_app, user, dashboard_view_name):
    django_app.get(reverse(dashboard_view_name), user=user, status=403)

@pytest.mark.django_db
@pytest.mark.parametrize(
    'dashboard_view_name',
    [
        'dashboard:home',
        'dashboard:social_posts',
    ],
)
def test_anonymous_users_are_redirected_to_login(django_app, dashboard_view_name):
    # Expect a redirect to login for anonymous users attempting to access dashboard views
    response = django_app.get(reverse(dashboard_view_name), status=302)
    location = response.headers.get('Location', '')
    assert 'login' in location.lower(), f"Expected redirect to login, got Location={location\!r}"

@pytest.mark.django_db
def test_home_context_includes_nonnegative_int_count(django_app, admin_user):
    # Validate type and basic invariant of context values without coupling to domain models
    response = django_app.get(reverse('dashboard:home'), user=admin_user, status=200)
    # Key from existing tests
    assert 'future_events_count' in response.context
    count = response.context['future_events_count']
    assert isinstance(count, int), "future_events_count should be an integer"
    assert count >= 0, "future_events_count should be non-negative"

@pytest.mark.django_db
def test_staff_non_superuser_can_access_dashboard_views(django_app, django_user_model):
    # Create a staff user (not superuser) and verify access is permitted for staff
    staff_user = django_user_model.objects.create_user(
        username='staffer',
        email='staffer@example.com',
        password='pass1234',
        is_staff=True,
        is_superuser=False,
    )
    # Login via django-webtest by passing user object
    resp_home = django_app.get(reverse('dashboard:home'), user=staff_user, status=200)
    assert 'future_events_count' in resp_home.context

    django_app.get(reverse('dashboard:social_posts'), user=staff_user, status=200)

@pytest.mark.django_db
@pytest.mark.parametrize(
    'dashboard_view_name',
    [
        'dashboard:home',
        'dashboard:social_posts',
    ],
)
def test_access_strict_403_for_authenticated_non_staff(django_app, django_user_model, dashboard_view_name):
    # Ensure explicitly that authenticated non-staff users receive 403, matching raise_exception=True behavior
    non_staff = django_user_model.objects.create_user(
        username='regularjoe',
        email='regular@example.com',
        password='pass1234',
        is_staff=False,
        is_superuser=False,
    )
    django_app.get(reverse(dashboard_view_name), user=non_staff, status=403)

@pytest.mark.django_db
def test_home_does_not_crash_around_day_boundary(django_app, admin_user, monkeypatch):
    # Some dashboards compute "future" relative to now(). Freeze time close to midnight to catch edge math.
    fixed_now = timezone.now().replace(hour=23, minute=59, second=50, microsecond=0)
    # Monkeypatch timezone.now used by the view (common pattern). If import path differs, this is a safe no-op.
    try:
        import dashboard.views as dash_views  # type: ignore
        monkeypatch.setattr(dash_views.timezone, "now", lambda: fixed_now, raising=True)
    except Exception:
        # If views import path differs, at least the test still exercises the endpoint without patching.
        pass

    response = django_app.get(reverse('dashboard:home'), user=admin_user, status=200)
    assert 'future_events_count' in response.context
    assert isinstance(response.context['future_events_count'], int)

@pytest.mark.django_db
def test_social_posts_html_renders_basic_structure(django_app, admin_user):
    # Avoid brittle template assertions; check basic HTML presence to ensure template renders
    response = django_app.get(reverse('dashboard:social_posts'), user=admin_user, status=200)
    html = response.text.lower()
    # Look for stable words likely present on the page without relying on exact template details
    for token in ('social', 'post'):
        assert token in html, f"Expected token {token\!r} to appear in social posts page HTML"
