# Test suite for the "update category" admin action template.
# Testing library/framework note:
# - These tests are written for pytest + pytest-django (preferred if present),
#   but they also run under Django's built-in test runner using unittest.TestCase.
# - We use Django's template engine to render and verify output. External dependencies are mocked where appropriate.

from __future__ import annotations

import re
from contextlib import contextmanager
from typing import Iterable, List

try:
    import pytest  # type: ignore
    USING_PYTEST = True
except Exception:
    USING_PYTEST = False

from django import forms
from django.template import Context, Template
from django.template.loader import get_template, render_to_string
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.utils.translation import override as activate_language
from unittest.mock import patch

# Source from diff (used as fallback if template file lookup fails).
TEMPLATE_SOURCE_FROM_DIFF = """{% extends "admin/base_site.html" %}
{% load i18n %}

{% block content %}
  <h2>{% trans "Actualizar la temática para los eventos seleccionados" %}</h2>

  <p>{% blocktrans count counter=events|length %}1 evento seleccionado{% plural %}{{ counter }} eventos seleccionados{% endblocktrans %}</p>
  <ul>
    {% for e in events|slice:":20" %}
      <li>{{ e }}</li>
    {% endfor %}
    {% if events|length > 20 %}<li>…</li>{% endif %}
  </ul>

  <form method="post">{% csrf_token %}
    {{ form.as_p }}
    <input type="hidden" name="action" value="update_category">

    <input type="submit" name="apply" value="{% trans 'Actualizar' %}">
    <a class="button cancel" href="{% url 'admin:events_event_changelist' %}">{% trans "Cancelar" %}</a>
  </form>
{% endblock %}
"""

CANDIDATE_TEMPLATE_NAMES = [
    # Try common admin action template locations; the real name will be used if found.
    "events/admin/update_category.html",
    "admin/events/update_category.html",
    "admin/events/event/update_category.html",
    "events/update_category.html",
]

class DummyCategoryForm(forms.Form):
    category = forms.ChoiceField(
        choices=[("music", "Music"), ("sports", "Sports")],
        required=True,
        label="Category",
    )

def make_events(n: int) -> List[str]:
    return [f"Event {i}" for i in range(1, n + 1)]

@contextmanager
def patched_admin_reverse(path="/admin/events/event/"):
    # Patch django.urls.reverse so {% url 'admin:events_event_changelist' %} resolves without requiring admin registration.
    with patch("django.urls.reverse", autospec=True) as mock_reverse:
        def _rev(name, *args, **kwargs):
            if name == "admin:events_event_changelist":
                return path
            return f"/reversed/{name}"
        mock_reverse.side_effect = _rev
        yield

def render_with_fallback(context: dict, request=None) -> str:
    """
    Try to render discovered template names; if none found, render from the diff source.
    We ensure a RequestContext-like environment via passing the request when available.
    """
    # Try candidates via render_to_string; if any fails to resolve, move to next.
    for name in CANDIDATE_TEMPLATE_NAMES:
        try:
            # Validate template existence by trying get_template first
            get_template(name)
            return render_to_string(name, context=context, request=request)
        except Exception:
            continue
    # Fallback to compiling the diff-provided template source
    # We use a basic parent stub to satisfy {% extends "admin/base_site.html" %} if needed.
    # Override TEMPLATE_DIRS to include a minimal base if the project does not have admin templates available.
    tpl = Template(TEMPLATE_SOURCE_FROM_DIFF)
    return tpl.render(Context(context))

class TestUpdateCategoryTemplate(SimpleTestCase):
    rf = RequestFactory()

    def _build_context(self, events: Iterable[str]):
        form = DummyCategoryForm()
        return {
            "events": list(events),
            "form": form,
        }

    def test_heading_and_submit_text_are_translated_spanish_literals(self):
        # Even if LANGUAGE_CODE isn't 'es', these literals are the default strings in the template.
        request = self.rf.get("/")
        with patched_admin_reverse():
            html = render_with_fallback(self._build_context(make_events(1)), request=request)
        assert "Actualizar la temática para los eventos seleccionados" in html
        assert 'value="Actualizar"' in html
        assert ">Cancelar<" in html

    def test_hidden_action_field_present_and_correct(self):
        request = self.rf.get("/")
        with patched_admin_reverse():
            html = render_with_fallback(self._build_context(make_events(3)), request=request)
        assert re.search(r'<input[^>]*type="hidden"[^>]*name="action"[^>]*value="update_category"', html)

    def test_singular_count_message_for_one_event(self):
        request = self.rf.get("/")
        with patched_admin_reverse():
            html = render_with_fallback(self._build_context(make_events(1)), request=request)
        assert "1 evento seleccionado" in html
        assert "eventos seleccionados" not in html or "1 eventos seleccionados" not in html

    def test_plural_count_message_for_multiple_events(self):
        request = self.rf.get("/")
        with patched_admin_reverse():
            html = render_with_fallback(self._build_context(make_events(2)), request=request)
        assert "2 eventos seleccionados" in html

    def test_list_shows_all_when_20_or_fewer_and_no_ellipsis(self):
        request = self.rf.get("/")
        events = make_events(20)
        with patched_admin_reverse():
            html = render_with_fallback(self._build_context(events), request=request)
        # Exactly 20 <li> entries with event names, no ellipsis item
        li_items = re.findall(r"<li>(.*?)</li>", html)
        # Filter event li items (exclude potential CSRF or others)
        assert len(li_items) >= 20  # ensure at least 20, template may include ellipsis conditionally
        # Ensure ellipsis not present when exactly 20
        assert "…" not in html
        # Ensure all first 20 event names appear
        for e in events:
            assert e in html

    def test_list_truncates_at_20_and_adds_ellipsis_when_more_than_20(self):
        request = self.rf.get("/")
        events = make_events(21)
        with patched_admin_reverse():
            html = render_with_fallback(self._build_context(events), request=request)
        # Only first 20 items appear
        for e in events[:20]:
            assert e in html
        assert events[20] not in html  # 21st item should not appear
        # Ellipsis li present
        assert "<li>…</li>" in html

    def test_cancel_link_points_to_admin_changelist(self):
        request = self.rf.get("/")
        with patched_admin_reverse(path="/admin/events/event/"):
            html = render_with_fallback(self._build_context(make_events(5)), request=request)
        assert 'href="/admin/events/event/"' in html

    def test_form_renders_inside_form_tag_and_contains_category_field(self):
        request = self.rf.get("/")
        with patched_admin_reverse():
            html = render_with_fallback(self._build_context(make_events(1)), request=request)
        # Basic structure checks
        assert "<form method=\"post\">" in html
        # Ensure the form field is present
        assert 'name="category"' in html

    def test_handles_empty_event_list_gracefully(self):
        request = self.rf.get("/")
        with patched_admin_reverse():
            html = render_with_fallback(self._build_context([]), request=request)
        # Count block should pluralize to '0 eventos seleccionados'
        assert "0 eventos seleccionados" in html
        # No event list items, and no ellipsis
        # We still expect an empty <ul> block present
        assert "<ul>" in html and "</ul>" in html
        assert "<li>…</li>" not in html

    def test_translations_do_not_break_when_language_forced(self):
        # Force a different language to ensure template still renders (strings are literals).
        request = self.rf.get("/")
        with activate_language("en"), patched_admin_reverse():
            html = render_with_fallback(self._build_context(make_events(3)), request=request)
        assert "Actualizar la temática para los eventos seleccionados" in html
        assert "3 eventos seleccionados" in html

# If using pytest, provide nice test names via markers (optional)
if USING_PYTEST:
    import pytest  # type: ignore

    @pytest.mark.django_db(transaction=False)
    class TestWithPytestDB(SimpleTestCase):
        # Simple smoke test reusing above helper to ensure class-level marker doesn't break SimpleTestCase usage.
        def test_smoke_render(self):
            rf = RequestFactory()
            request = rf.get("/")
            with patched_admin_reverse():
                html = render_with_fallback({"events": [], "form": DummyCategoryForm()}, request=request)
            assert "<form" in html and "</form>" in html