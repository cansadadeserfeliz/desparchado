from unittest import mock
import types

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.http import HttpRequest, QueryDict
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
import pytest

# Import the ModelAdmin classes from events.admin
from events import admin as events_admin
from events.models import Event, Organizer, SocialNetworkPost, Speaker


class DummySite(AdminSite):
    site_header = "Test Admin"


# Common setup mixin
class AdminTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.superuser = cls.User.objects.create_user(
            username="super", email="super@example.com", password="x", is_superuser=True, is_staff=True
        )
        cls.staff = cls.User.objects.create_user(
            username="staff", email="staff@example.com", password="x", is_superuser=False, is_staff=True
        )

    def rf_as(self, user, method="get", path="/admin/", data=None):
        rf = RequestFactory()
        req = getattr(rf, method.lower())(path, data=data or {})
        req.user = user
        # Django admin expects a few attrs sometimes
        req._messages = mock.MagicMock()
        return req


class TestSocialNetworkPostAdmin(AdminTestMixin, TestCase):
    def setUp(self):
        self.site = DummySite()
        self.admin = events_admin.SocialNetworkPostAdmin(SocialNetworkPost, self.site)
        # Minimal event to relate post
        self.event = Event.objects.create(
            title="E1", slug="e1", description="d", event_date="2099-01-01", category=Event.Category.talk
        )

    def test_save_model_sets_created_by_on_create(self):
        req = self.rf_as(self.staff, "post")
        post = SocialNetworkPost(event=self.event, description="desc")
        self.assertIsNone(post.id)
        form = mock.MagicMock()
        self.admin.save_model(req, post, form, change=False)
        self.assertEqual(post.created_by, self.staff)

    def test_save_model_preserves_created_by_on_update(self):
        post = SocialNetworkPost.objects.create(event=self.event, description="d", created_by=self.superuser)
        req = self.rf_as(self.staff, "post")
        form = mock.MagicMock()
        self.admin.save_model(req, post, form, change=True)
        # created_by should remain as initially set (save_model only sets on create)
        self.assertEqual(post.created_by, self.superuser)


class TestEventAdmin(AdminTestMixin, TestCase):
    def setUp(self):
        self.site = DummySite()
        self.admin = events_admin.EventAdmin(Event, self.site)
        self.event1 = Event.objects.create(
            title="E1", slug="e1", description="d", event_date="2099-01-01", category=Event.Category.talk
        )
        self.event2 = Event.objects.create(
            title="E2", slug="e2", description="d", event_date="2099-01-02", category=Event.Category.workshop
        )

    def test_get_actions_removes_delete_selected(self):
        req = self.rf_as(self.superuser)
        actions = self.admin.get_actions(req)
        # delete_selected is removed
        self.assertNotIn("delete_selected", actions)
        self.assertIn("update_category", actions)

    def test_get_readonly_fields(self):
        req = self.rf_as(self.superuser)
        readonly = self.admin.get_readonly_fields(req, obj=self.event1)
        self.assertEqual(readonly, ["slug"])

    def test_has_delete_permission_depends_on_superuser(self):
        req_super = self.rf_as(self.superuser)
        req_staff = self.rf_as(self.staff)
        self.assertTrue(self.admin.has_delete_permission(req_super, obj=self.event1))
        self.assertFalse(self.admin.has_delete_permission(req_staff, obj=self.event1))

    def test_save_model_sets_created_by_on_create(self):
        req = self.rf_as(self.staff, "post")
        event = Event(
            title="E3", slug="e3", description="d", event_date="2099-01-03", category=Event.Category.other
        )
        self.admin.save_model(req, event, form=mock.MagicMock(), change=False)
        self.assertEqual(event.created_by, self.staff)

    def test_update_category_get_renders_form_with_selected_ids(self):
        # Simulate GET of action page: when "apply" not in POST, admin renders template
        req = self.rf_as(self.superuser, "post")
        # No "apply" key -> enters else branch creating a form with initial selected IDs
        # Build a queryset with selected events
        qs = Event.objects.filter(id__in=[self.event1.id, self.event2.id])
        resp = self.admin.update_category(req, qs)
        # The view returns a rendered TemplateResponse; since admin uses render shortcut, it returns HttpResponse
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Actualizar tem\xc3\xa1tica", resp.content)  # title is translated Spanish string
        # Ensure the two selected ids are present in the HTML as hidden inputs
        self.assertIn(str(self.event1.id).encode(), resp.content)
        self.assertIn(str(self.event2.id).encode(), resp.content)

    def test_update_category_post_apply_updates_and_redirects(self):
        req = self.rf_as(self.superuser, "post")
        qd = QueryDict(mutable=True)
        qd.update(
            {
                "_selected_action": [str(self.event1.id), str(self.event2.id)],
                "category": str(Event.Category.meetup),
                "apply": "1",
            }
        )
        req.POST = qd
        qs = Event.objects.filter(id__in=[self.event1.id, self.event2.id])
        with mock.patch.object(self.admin, "message_user") as message_user:
            resp = self.admin.update_category(req, qs)
        # Redirect back to changelist
        self.assertEqual(resp.status_code, 302)
        # Both instances updated
        self.event1.refresh_from_db()
        self.event2.refresh_from_db()
        self.assertEqual(self.event1.category, Event.Category.meetup)
        self.assertEqual(self.event2.category, Event.Category.meetup)
        message_user.assert_called()  # "2 events updated"

    def test_update_category_invalid_post_rerenders_form(self):
        # Missing category -> invalid form -> render template
        req = self.rf_as(self.superuser, "post", data={"apply": "1"})
        qs = Event.objects.filter(id=self.event1.id)
        resp = self.admin.update_category(req, qs)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'name="category"', resp.content)

    def test_save_formset_sets_created_by_on_inline_instances_and_calls_save_m2m(self):
        req = self.rf_as(self.staff, "post")
        # Prepare two unsaved inline instances
        inst1 = SocialNetworkPost(event=self.event1, description="a")
        inst2 = SocialNetworkPost(event=self.event1, description="b")

        # Fake formset with the API used in save_formset
        fake_formset = types.SimpleNamespace()

        def save(commit=False):
            assert commit is False
            return [inst1, inst2]

        fake_formset.save = save
        fake_formset.save_m2m = mock.MagicMock()

        # Exercise
        self.admin.save_formset(req, form=mock.MagicMock(), formset=fake_formset, change=False)

        inst1.refresh_from_db()
        inst2.refresh_from_db()
        self.assertEqual(inst1.created_by, self.staff)
        self.assertEqual(inst2.created_by, self.staff)
        fake_formset.save_m2m.assert_called_once()


class TestOrganizerAdmin(AdminTestMixin, TestCase):
    def setUp(self):
        self.site = DummySite()
        self.admin = events_admin.OrganizerAdmin(Organizer, self.site)

    def test_save_model_sets_created_by_on_create(self):
        req = self.rf_as(self.staff, "post")
        organizer = Organizer(name="Org", slug="org", description="d")
        self.admin.save_model(req, organizer, form=mock.MagicMock(), change=False)
        self.assertEqual(organizer.created_by, self.staff)


class TestSpeakerAdmin(AdminTestMixin, TestCase):
    def setUp(self):
        self.site = DummySite()
        self.admin = events_admin.SpeakerAdmin(Speaker, self.site)

    def test_save_model_sets_created_by_and_notifies_for_non_superuser(self):
        req = self.rf_as(self.staff, "post")
        speaker = Speaker(name="Alice", slug="alice", description="bio")
        with mock.patch("events.admin.send_admin_notification") as notify:
            self.admin.save_model(req, speaker, form=mock.MagicMock(), change=False)
            self.assertEqual(speaker.created_by, self.staff)
            notify.assert_called_once()

    def test_save_model_skips_notification_for_superuser(self):
        req = self.rf_as(self.superuser, "post")
        speaker = Speaker(name="Bob", slug="bob", description="bio")
        with mock.patch("events.admin.send_admin_notification") as notify:
            self.admin.save_model(req, speaker, form=mock.MagicMock(), change=False)
            notify.assert_not_called()

    def test_get_actions_returns_empty(self):
        req = self.rf_as(self.superuser)
        self.assertEqual(self.admin.get_actions(req), [])

    def test_has_add_permission_true(self):
        req = self.rf_as(self.staff)
        self.assertTrue(self.admin.has_add_permission(req))

    def test_has_delete_permission_depends_on_superuser(self):
        req_staff = self.rf_as(self.staff)
        req_super = self.rf_as(self.superuser)
        self.assertFalse(self.admin.has_delete_permission(req_staff))
        self.assertTrue(self.admin.has_delete_permission(req_super))


class TestCategoryUpdateForm(TestCase):
    def test_choices_match_event_category(self):
        form = events_admin.CategoryUpdateForm()
        event_choices = list(Event.Category.choices)
        self.assertEqual(list(form.fields["category"].choices), event_choices)