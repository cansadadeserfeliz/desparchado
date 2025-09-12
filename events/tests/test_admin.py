import types
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory
from django.utils import timezone

# Import admin classes and models under test
import events.admin as events_admin
from events.models import Event, Organizer, Speaker, SocialNetworkPost

User = get_user_model()


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def admin_site():
    return AdminSite()


@pytest.fixture
def superuser(db):
    return User.objects.create_user(
        username="super", email="super@example.com", password="x", is_superuser=True, is_staff=True
    )


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff", email="staff@example.com", password="x", is_superuser=False, is_staff=True
    )


@pytest.fixture
def event(db, superuser):
    # Create minimal Event; fill fields conditionally if required by model
    defaults = {}
    # Common fields used by list_display/ordering but not required for creation
    defaults.setdefault("title", "Sample Event")
    defaults.setdefault("slug", "sample-event")
    defaults.setdefault("event_date", timezone.now().date())
    # Category: prefer first choice if available
    try:
        choices = list(Event.Category.choices)  # type: ignore[attr-defined]
        defaults.setdefault("category", choices[0][0] if choices else None)
    except Exception:
        pass
    # Flags
    for f in ("is_published", "is_approved", "is_hidden", "is_featured_on_homepage"):
        if hasattr(Event, f):
            defaults.setdefault(f, False)
    obj = Event.objects.create(created_by=superuser, **defaults)
    return obj


class _ReqObj(types.SimpleNamespace):
    """Helper to mimic request with POST/GET and user."""

def _make_request(rf, user, method="get", data=None, path="/admin/events/event/"):
    req = getattr(rf, method.lower())(path, data=data or {})
    req.user = user
    # AdminSite.each_context reads req; message_user may attempt messages framework.
    # We patch message_user in tests that exercise it.
    return req


@pytest.mark.django_db
def test_social_network_post_admin_sets_created_by_on_create(rf, admin_site, staff_user, event):
    admin_obj = events_admin.SocialNetworkPostAdmin(SocialNetworkPost, admin_site)
    post = SocialNetworkPost(event=event, description="desc", published_at=timezone.now())
    req = _make_request(rf, staff_user, "post")
    assert post.pk is None
    admin_obj.save_model(req, post, form=None, change=False)
    assert post.pk is not None
    assert post.created_by == staff_user


@pytest.mark.django_db
def test_event_admin_get_actions_removes_delete_selected(rf, admin_site, superuser):
    admin_obj = events_admin.EventAdmin(Event, admin_site)
    req = _make_request(rf, superuser, "get")
    actions = admin_obj.get_actions(req)
    assert "delete_selected" not in actions


@pytest.mark.django_db
def test_event_admin_update_category_get_renders_form_with_selected_ids(rf, admin_site, superuser, event, django_assert_num_queries):
    admin_obj = events_admin.EventAdmin(Event, admin_site)
    qs = Event.objects.filter(pk__in=[event.pk])
    req = _make_request(rf, superuser, "get", path="/admin/events/event/?action=update_category")
    # Patch render to avoid requiring template file; capture context
    with patch.object(events_admin, "render", autospec=True) as mock_render:
        mock_render.return_value = HttpResponse("ok")
        resp = admin_obj.update_category(req, qs)
    assert resp.status_code == 200
    assert mock_render.called
    _, args, kwargs = mock_render.mock_calls[0]
    # args: (request, template_name, context)
    context = args[2]
    assert "form" in context and "events" in context
    # Initial should include selected ids
    initial_ids = set(context["form"].initial.get("_selected_action", []))
    assert event.pk in initial_ids


@pytest.mark.django_db
def test_event_admin_update_category_post_applies_selection_and_redirects(rf, admin_site, superuser, event):
    admin_obj = events_admin.EventAdmin(Event, admin_site)
    qs = Event.objects.filter(pk=event.pk)
    # Choose a different category if possible, else reuse current
    try:
        categories = list(Event.Category.choices)  # type: ignore[attr-defined]
        target = categories[-1][0] if categories else getattr(event, "category", None)
    except Exception:
        target = getattr(event, "category", None)
    data = {"apply": "1", "category": target}
    req = _make_request(rf, superuser, "post", data=data, path="/admin/events/event/?action=update_category")
    # Avoid messages framework dependency
    with patch.object(events_admin.EventAdmin, "message_user", autospec=True) as mock_msg:
        resp = admin_obj.update_category(req, qs)
    assert resp.status_code in (301, 302)
    event.refresh_from_db()
    if target is not None and hasattr(event, "category"):
        assert event.category == target
    mock_msg.assert_called_once()
    # message text contains "events updated"
    assert "updated" in str(mock_msg.call_args[0][-1]).lower()


@pytest.mark.django_db
def test_event_admin_save_formset_sets_created_by_and_saves_m2m(rf, admin_site, staff_user, event):
    admin_obj = events_admin.EventAdmin(Event, admin_site)
    req = _make_request(rf, staff_user, "post")
    # Build fake formset returning unsaved instances
    inst1 = SocialNetworkPost(event=event, description="a", published_at=timezone.now())
    inst2 = SocialNetworkPost(event=event, description="b", published_at=timezone.now())
    formset = MagicMock()
    formset.save.return_value = None
    formset.save_m2m.return_value = None
    formset.save.side_effect = [ [inst1, inst2] ]  # when called with commit=False
    def _save(commit=True):
        if not commit:
            return [inst1, inst2]
        return None
    formset.save = MagicMock(side_effect=lambda commit=False: _save(commit))
    admin_obj.save_formset(req, form=None, formset=formset, change=False)
    for inst in (inst1, inst2):
        assert inst.pk is not None
        assert inst.created_by == staff_user
    formset.save_m2m.assert_called_once()


@pytest.mark.django_db
def test_event_admin_save_model_sets_created_by_on_create(rf, admin_site, staff_user):
    admin_obj = events_admin.EventAdmin(Event, admin_site)
    req = _make_request(rf, staff_user, "post")
    data = {"title": "X", "slug": "x", "event_date": timezone.now().date()}
    try:
        choices = list(Event.Category.choices)  # type: ignore[attr-defined]
        data["category"] = choices[0][0] if choices else None
    except Exception:
        pass
    ev = Event(**{k: v for k, v in data.items() if hasattr(Event, k)})
    assert ev.pk is None
    admin_obj.save_model(req, ev, form=None, change=False)
    assert ev.pk is not None
    assert ev.created_by == staff_user


def test_event_admin_readonly_fields_only_slug(rf, admin_site, superuser):
    admin_obj = events_admin.EventAdmin(Event, admin_site)
    req = _make_request(rf, superuser, "get")
    ro = admin_obj.get_readonly_fields(req)
    assert ro == ["slug"]


def test_event_admin_has_delete_permission_reflects_superuser(rf, admin_site, superuser, staff_user):
    admin_obj = events_admin.EventAdmin(Event, admin_site)
    req_su = _make_request(rf, superuser, "get")
    req_staff = _make_request(rf, staff_user, "get")
    assert admin_obj.has_delete_permission(req_su) is True
    assert admin_obj.has_delete_permission(req_staff) is False


@pytest.mark.django_db
def test_organizer_admin_save_model_sets_created_by_on_create(rf, admin_site, staff_user):
    admin_obj = events_admin.OrganizerAdmin(Organizer, admin_site)
    req = _make_request(rf, staff_user, "post")
    org = Organizer(name="Org Name", slug="org-name") if hasattr(Organizer, "slug") else Organizer(name="Org Name")
    assert org.pk is None
    admin_obj.save_model(req, org, form=None, change=False)
    assert org.pk is not None
    assert org.created_by == staff_user


@pytest.mark.django_db
def test_speaker_admin_save_model_sets_created_by_and_notifies_non_superuser(rf, admin_site, staff_user):
    admin_obj = events_admin.SpeakerAdmin(Speaker, admin_site)
    req = _make_request(rf, staff_user, "post")
    spk = Speaker(name="Speaker Name", slug="speaker-name") if hasattr(Speaker, "slug") else Speaker(name="Speaker Name")
    with patch("events.admin.send_admin_notification", autospec=True) as mock_notify:
        admin_obj.save_model(req, spk, form=None, change=False)
    assert spk.pk is not None
    assert spk.created_by == staff_user
    mock_notify.assert_called_once()


@pytest.mark.django_db
def test_speaker_admin_save_model_does_not_notify_superuser(rf, admin_site, superuser):
    admin_obj = events_admin.SpeakerAdmin(Speaker, admin_site)
    req = _make_request(rf, superuser, "post")
    spk = Speaker(name="Speaker Name", slug="speaker-name") if hasattr(Speaker, "slug") else Speaker(name="Speaker Name")
    with patch("events.admin.send_admin_notification", autospec=True) as mock_notify:
        admin_obj.save_model(req, spk, form=None, change=False)
    mock_notify.assert_not_called()


def test_speaker_admin_actions_empty(rf, admin_site, superuser):
    admin_obj = events_admin.SpeakerAdmin(Speaker, admin_site)
    req = _make_request(rf, superuser, "get")
    assert admin_obj.get_actions(req) == {}


def test_speaker_admin_permissions(rf, admin_site, superuser):
    admin_obj = events_admin.SpeakerAdmin(Speaker, admin_site)
    assert admin_obj.has_add_permission(_make_request(rf, superuser, "get")) is True
    assert admin_obj.has_delete_permission(_make_request(rf, superuser, "get")) is True