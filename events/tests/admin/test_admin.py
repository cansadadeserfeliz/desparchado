"""
Tests for events.admin module (admin classes and actions).

Note on framework:
- These tests use Django's built-in TestCase and RequestFactory with unittest.mock.
- They are compatible with pytest if the project uses pytest-django.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

import events.admin as events_admin
from events.admin import (
    EventAdmin,
    OrganizerAdmin,
    SpeakerAdmin,
    SocialNetworkPostAdmin,
)
from events.models import Event, Speaker, Organizer, SocialNetworkPost


def _any_valid_category():
    """
    Returns a valid category value from Event.Category.choices
    without hardcoding any specific option.
    """
    # Event.Category is expected to be a Django Choices/Enum with .choices
    choices = getattr(Event.Category, "choices", None)
    if choices:
        return choices[0][0]
    # Fallback to first enum value if using TextChoices (has .values)
    values = getattr(Event.Category, "values", None)
    if values:
        return list(values)[0]
    # Ultimate fallback (should not normally happen)
    return None


class TestEventAdmin(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.superuser = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="pwd",
            is_staff=True,
            is_superuser=True,
        )
        cls.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="pwd",
            is_staff=True,
            is_superuser=False,
        )

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = EventAdmin(Event, admin.site)

    def test_get_actions_excludes_delete_selected_and_includes_update(self):
        request = self.factory.get("/")
        request.user = self.superuser
        actions = self.admin.get_actions(request)
        self.assertIsInstance(actions, dict)
        self.assertNotIn("delete_selected", actions)
        # ensure custom action is exposed
        self.assertIn("update_category", actions)

    @patch("events.admin.redirect")
    def test_update_category_apply_valid_updates_queryset_and_redirects(
        self, mock_redirect
    ):
        # Arrange
        category_value = _any_valid_category()
        if category_value is None:
            self.skipTest("Event.Category choices not available")

        mock_redirect.side_effect = lambda req: "REDIRECTED"

        request = self.factory.post(
            "/admin/events/event/",
            data={
                "apply": "1",
                "_selected_action": "1",  # required by the form
                "category": category_value,
            },
        )
        request.user = self.superuser

        queryset = MagicMock()
        queryset.update.return_value = 2  # simulate two rows updated

        # Avoid dependence on Django messages framework internals
        self.admin.message_user = MagicMock()

        # Act
        result = self.admin.update_category(request, queryset)

        # Assert
        self.assertEqual(result, "REDIRECTED")
        queryset.update.assert_called_once_with(category=category_value)
        self.admin.message_user.assert_called_once()
        # Message should contain the count
        args, kwargs = self.admin.message_user.call_args
        self.assertIn("2 events updated", args[1])

    def test_update_category_initial_renders_form_with_selected_ids(self):
        # Arrange
        ids = [10, 20, 30]
        queryset = MagicMock()
        queryset.values_list.return_value = ids

        captured = {}

        def fake_render(request, template, context):
            captured["template"] = template
            captured["context"] = context
            # Return the context for easy assertions on return value
            return context

        request = self.factory.post("/admin/events/event/", data={})
        request.user = self.superuser

        # Act
        with patch.object(events_admin, "render", side_effect=fake_render):
            result = self.admin.update_category(request, queryset)

        # Assert
        self.assertIs(result, captured["context"])
        self.assertEqual(
            captured["template"], "events/admin/update_category.html"
        )
        form = captured["context"]["form"]
        self.assertIn("_selected_action", form.initial)
        self.assertEqual(list(form.initial["_selected_action"]), ids)
        # ensure standard admin context keys merged
        self.assertIn("opts", captured["context"])
        self.assertIn("title", captured["context"])

    def test_save_formset_sets_created_by_and_calls_save_m2m(self):
        request = self.factory.post("/")
        request.user = self.staff

        class _FakeInstance:
            def __init__(self):
                self.created_by = None
                self.saved = False

            def save(self):
                self.saved = True

        instances = [_FakeInstance(), _FakeInstance()]

        class _FakeFormSet:
            def __init__(self, _instances):
                self._instances = _instances
                self.m2m_saved = False

            def save(self, commit=False):
                if not commit:
                    return self._instances
                return []

            def save_m2m(self):
                self.m2m_saved = True

        formset = _FakeFormSet(instances)

        # Act
        self.admin.save_formset(request, form=None, formset=formset, change=False)

        # Assert created_by set and instance saved
        for inst in instances:
            self.assertIs(inst.created_by, request.user)
            self.assertTrue(inst.saved)
        self.assertTrue(formset.m2m_saved)

    def test_save_model_sets_created_by_on_create(self):
        request = self.factory.post("/")
        request.user = self.staff

        obj = SimpleNamespace(id=None, created_by=None)

        with patch(
            "django.contrib.admin.options.ModelAdmin.save_model", autospec=True
        ) as mock_super_save:
            self.admin.save_model(request, obj, form=None, change=False)

        self.assertIs(obj.created_by, request.user)
        mock_super_save.assert_called()

    def test_get_readonly_fields_returns_slug(self):
        request = self.factory.get("/")
        fields = self.admin.get_readonly_fields(request)
        self.assertEqual(fields, ["slug"])

    def test_has_delete_permission_respects_superuser(self):
        request = self.factory.get("/")
        request.user = self.staff
        self.assertFalse(self.admin.has_delete_permission(request))

        request.user = self.superuser
        self.assertTrue(self.admin.has_delete_permission(request))


class TestOrganizerAdmin(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user(
            username="org_staff",
            email="org_staff@example.com",
            password="pwd",
            is_staff=True,
            is_superuser=False,
        )

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = OrganizerAdmin(Organizer, admin.site)

    def test_save_model_sets_created_by_on_create(self):
        request = self.factory.post("/")
        request.user = self.staff
        obj = SimpleNamespace(id=None, created_by=None)

        with patch(
            "django.contrib.admin.options.ModelAdmin.save_model", autospec=True
        ) as mock_super_save:
            self.admin.save_model(request, obj, form=None, change=False)

        self.assertIs(obj.created_by, request.user)
        mock_super_save.assert_called()


class TestSpeakerAdmin(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.superuser = User.objects.create_user(
            username="speaker_admin",
            email="speaker_admin@example.com",
            password="pwd",
            is_staff=True,
            is_superuser=True,
        )
        cls.staff = User.objects.create_user(
            username="speaker_staff",
            email="speaker_staff@example.com",
            password="pwd",
            is_staff=True,
            is_superuser=False,
        )

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = SpeakerAdmin(Speaker, admin.site)

    def test_get_actions_returns_empty_list(self):
        request = self.factory.get("/")
        request.user = self.superuser
        actions = self.admin.get_actions(request)
        self.assertEqual(actions, [])

    def test_has_add_permission_always_true(self):
        request = self.factory.get("/")
        request.user = self.staff
        self.assertTrue(self.admin.has_add_permission(request))

    def test_has_delete_permission_respects_superuser(self):
        request = self.factory.get("/")
        request.user = self.staff
        self.assertFalse(self.admin.has_delete_permission(request))

        request.user = self.superuser
        self.assertTrue(self.admin.has_delete_permission(request))

    def test_save_model_sets_created_by_and_notifies_when_not_superuser(self):
        request = self.factory.post("/")
        request.user = self.staff
        obj = SimpleNamespace(id=None, created_by=None)

        with patch(
            "django.contrib.admin.options.ModelAdmin.save_model", autospec=True
        ) as mock_super_save, patch.object(
            events_admin, "send_admin_notification"
        ) as mock_notify:
            self.admin.save_model(request, obj, form=None, change=False)

        self.assertIs(obj.created_by, request.user)
        mock_super_save.assert_called()
        mock_notify.assert_called_once_with(request, obj, None, False)

    def test_save_model_does_not_notify_when_superuser(self):
        request = self.factory.post("/")
        request.user = self.superuser
        obj = SimpleNamespace(id=None, created_by=None)

        with patch(
            "django.contrib.admin.options.ModelAdmin.save_model", autospec=True
        ) as mock_super_save, patch.object(
            events_admin, "send_admin_notification"
        ) as mock_notify:
            self.admin.save_model(request, obj, form=None, change=False)

        self.assertIs(obj.created_by, request.user)
        mock_super_save.assert_called()
        mock_notify.assert_not_called()


class TestSocialNetworkPostAdmin(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user(
            username="snp_staff",
            email="snp_staff@example.com",
            password="pwd",
            is_staff=True,
            is_superuser=False,
        )

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = SocialNetworkPostAdmin(SocialNetworkPost, admin.site)

    def test_save_model_sets_created_by_on_create(self):
        request = self.factory.post("/")
        request.user = self.staff
        obj = SimpleNamespace(id=None, created_by=None)

        with patch(
            "django.contrib.admin.options.ModelAdmin.save_model", autospec=True
        ) as mock_super_save:
            self.admin.save_model(request, obj, form=None, change=False)

        self.assertIs(obj.created_by, request.user)
        mock_super_save.assert_called()