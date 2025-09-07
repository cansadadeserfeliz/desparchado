import io
import json
from types import SimpleNamespace
from datetime import datetime, timezone as dt_timezone

import pytest

from unittest.mock import MagicMock, patch, call

from django.utils import timezone
from django.conf import settings

# Import models; tests assume these apps exist
from events.models import Event, Organizer
from places.models import Place

# Import module under test
# If the module path differs, adjust this import accordingly.
from dashboard import spreadsheet_sync as ss


# ------------------------------------------------------------------------------
# Test framework note:
# These tests are written for pytest with pytest-django.
# If the project uses unittest.TestCase, they should still run under pytest,
# but can be adapted to Django TestCase by wrapping in classes if needed.
# ------------------------------------------------------------------------------

@pytest.fixture
def credentials_file_ok(monkeypatch, tmp_path):
    """
    Provide a temporary spreadsheet_credentials.json that can be opened and parsed.
    """
    data = {"type": "service_account", "project_id": "test"}
    p = tmp_path / "spreadsheet_credentials.json"
    p.write_text(json.dumps(data), encoding="utf-8")

    # Point BASE_DIR to tmp_path so the code opens our file
    monkeypatch.setattr(settings, "BASE_DIR", tmp_path, raising=False)

    # Patch Path.open to read from our temp file (but only when targeting that exact path)
    # Since the code uses: settings.BASE_DIR / "spreadsheet_credentials.json"
    # simply returning a normal open works because file exists at that exact path.
    return p


@pytest.fixture
def gspread_mocks():
    """
    Build a fake gspread client graph: gc -> spreadsheet -> sheet.
    Return dict containing the mocks and a helper to adjust rows.
    """
    sheet = MagicMock()
    spreadsheet = MagicMock()
    spreadsheet.get_worksheet.return_value = sheet
    gc = MagicMock()
    gc.open_by_key.return_value = spreadsheet
    return {"gc": gc, "spreadsheet": spreadsheet, "sheet": sheet}


@pytest.fixture
def fake_request_user(db, django_user_model):
    return django_user_model.objects.create(username="importer")


def _mk_row(
    title="My Event",
    date_str="2025-01-02 18:30",
    place="The Venue",
    category="talk",
    description="<b>Hello</b>",
    url="https://example.com/event",
    image="https://example.com/image.png",
    organizers="Org A, Org B",
):
    # Spreadsheet columns B..I (the code indexes those):
    # B: title, C: date, D: place, E: category, F: html, G: url, H: image, I: organizers
    return ["IGNORED-A", title, date_str, place, category, description, url, image, organizers]


# -----------------------------
# _get_cell_data
# -----------------------------

def test_get_cell_data_trims_and_maps_letters():
    row = ["A", "  B  ", " C ", ""]
    assert ss._get_cell_data(row, "A") == "A"
    assert ss._get_cell_data(row, "B") == "B"
    assert ss._get_cell_data(row, "C") == "C"
    assert ss._get_cell_data(row, "D") == ""  # empty string preserved
    assert ss._get_cell_data(row, "Z") == ""  # out of range returns empty


# -----------------------------
# save_image
# -----------------------------

class DummyImageField:
    def __init__(self):
        self.saved_as = None
        self.saved_content = None

    def save(self, name, content, save=True):
        self.saved_as = name
        self.saved_content = content.read() if hasattr(content, "read") else content


class DummyEvent(SimpleNamespace):
    pass


def _mk_dummy_event(slug="my-event"):
    return DummyEvent(slug=slug, image=DummyImageField())


@patch("dashboard.spreadsheet_sync.requests.get")
def test_save_image_logs_and_returns_on_status_not_200(mock_get, caplog):
    mock_get.return_value.status_code = 404
    mock_get.return_value.headers = {"Content-Type": "image/png"}
    mock_get.return_value.content = b""

    ev = _mk_dummy_event()
    ss.save_image(ev, "http://x/y.png")

    # Should have warned and not saved
    assert any("Image fetch failed" in rec.message for rec in caplog.records)
    assert ev.image.saved_as is None
    mock_get.assert_called_once_with("http://x/y.png", timeout=10)


@patch("dashboard.spreadsheet_sync.requests.get")
def test_save_image_rejects_non_image_content_type(mock_get, caplog):
    mock_get.return_value.status_code = 200
    mock_get.return_value.headers = {"Content-Type": "text/html; charset=utf-8"}
    mock_get.return_value.content = b"<html/>"

    ev = _mk_dummy_event()
    ss.save_image(ev, "http://x/y")

    assert any("Non-image content-type" in rec.message for rec in caplog.records)
    assert ev.image.saved_as is None


@patch("dashboard.spreadsheet_sync.requests.get")
def test_save_image_ok_png_extension_and_saves(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.headers = {"Content-Type": "image/png; charset=binary"}
    mock_get.return_value.content = b"\x89PNG...."

    ev = _mk_dummy_event(slug="great-event")
    ss.save_image(ev, "http://x/y.png")

    # Uses mimetypes.guess_extension; for image/png this should be ".png"
    assert ev.image.saved_as == "great-event.png"
    assert ev.image.saved_content == b"\x89PNG...."


@patch("dashboard.spreadsheet_sync.requests.get", side_effect=Exception("net down"))
def test_save_image_request_exception_is_logged(mock_get, caplog):
    ev = _mk_dummy_event()
    ss.save_image(ev, "http://x/broken")
    assert any("Image download error" in rec.message for rec in caplog.records)
    assert ev.image.saved_as is None


# -----------------------------
# sync_events
# -----------------------------

def _install_gspread(monkeypatch, gspread_mocks):
    # Patch service_account_from_dict to return our gc
    monkeypatch.setattr(ss.gspread, "service_account_from_dict", lambda creds: gspread_mocks["gc"])
    return gspread_mocks


def _wire_sheet_rows(gspread_mocks, rows):
    gspread_mocks["sheet"].get.return_value = rows


def _assert_event_basics(ev, title, category, place_obj, dt_expected):
    assert ev.title == title
    assert ev.category == category
    assert ev.place_id == place_obj.id
    assert ev.event_date == dt_expected
    assert ev.is_published is True
    assert ev.is_approved is True


def test_sync_events_returns_error_when_credentials_missing(monkeypatch, tmp_path):
    # No credentials file present
    monkeypatch.setattr(settings, "BASE_DIR", tmp_path, raising=False)
    res = ss.sync_events("sheet", 0, "B2:I2", request_user=None)
    assert res == [dict(error="Spreadsheet credentials could not be loaded")]


def test_sync_events_returns_error_when_credentials_bad_json(monkeypatch, tmp_path):
    creds_path = tmp_path / "spreadsheet_credentials.json"
    creds_path.write_text("{BAD JSON", encoding="utf-8")
    monkeypatch.setattr(settings, "BASE_DIR", tmp_path, raising=False)
    res = ss.sync_events("sheet", 0, "B2:I2", request_user=None)
    assert res == [dict(error="Spreadsheet credentials could not be loaded")]


@pytest.mark.django_db
def test_sync_events_invalid_event_date_is_reported(credentials_file_ok, monkeypatch, gspread_mocks, fake_request_user):
    _install_gspread(monkeypatch, gspread_mocks)

    # Row with invalid date in column C
    bad_row = _mk_row(date_str="not-a-date")
    _wire_sheet_rows(gspread_mocks, [bad_row])

    res = ss.sync_events("sheet", 0, "B2:I2", request_user=fake_request_user)
    assert res[0]["data"] == bad_row
    assert res[0]["error"] == 'Invalid event_date: "not-a-date"'


@pytest.mark.django_db
def test_sync_events_place_not_found_error(credentials_file_ok, monkeypatch, gspread_mocks, fake_request_user):
    _install_gspread(monkeypatch, gspread_mocks)
    _wire_sheet_rows(gspread_mocks, [_mk_row(place="Unknown Venue")])

    res = ss.sync_events("sheet", 0, "B2:I2", request_user=fake_request_user)
    assert 'Place "Unknown Venue" not found' in res[0]["error"]


@pytest.mark.django_db
def test_sync_events_organizer_missing_yields_error_and_event_created(
    credentials_file_ok, monkeypatch, gspread_mocks, fake_request_user
):
    venue = Place.objects.create(name="The Venue")

    # Only Org A exists; Org B will be missing
    org_a = Organizer.objects.create(name="Org A")

    _install_gspread(monkeypatch, gspread_mocks)
    row = _mk_row(organizers="Org A, Org B")
    _wire_sheet_rows(gspread_mocks, [row])

    with patch.object(ss, "save_image") as mock_save_img:
        res = ss.sync_events("sheet", 0, "B2:I2", request_user=fake_request_user)

    # Expect two entries: one error for missing organizer and one success for the event
    assert any(item.get("error") == 'Organizer "Org B" not found' for item in res)
    success_items = [it for it in res if "event" in it]
    assert len(success_items) == 1
    event_item = success_items[0]
    ev = event_item["event"]

    # Verify event fields
    parsed_dt = timezone.make_aware(timezone.datetime(2025, 1, 2, 18, 30)) if getattr(settings, "USE_TZ", False) \
        else datetime(2025, 1, 2, 18, 30)
    _assert_event_basics(ev, "My Event", "talk", venue, parsed_dt)
    # Only existing organizer attached
    assert list(ev.organizers.all()) == [org_a]
    # Image helper called
    mock_save_img.assert_called_once()


@pytest.mark.django_db
def test_sync_events_success_create_sets_created_by_and_updates_on_second_run(
    credentials_file_ok, monkeypatch, gspread_mocks, fake_request_user
):
    Place.objects.create(name="The Venue")
    Organizer.objects.create(name="Org A")

    _install_gspread(monkeypatch, gspread_mocks)
    row = _mk_row(organizers="Org A")
    _wire_sheet_rows(gspread_mocks, [row])

    # First run -> created True
    with patch.object(ss, "save_image") as mock_save_img:
        res1 = ss.sync_events("sheet", 0, "B2:I2", request_user=fake_request_user)
    assert res1 and res1[0]["created"] is True
    ev1 = res1[0]["event"]
    assert ev1.created_by_id == fake_request_user.id
    mock_save_img.assert_called_once()

    # Second run with an updated title should yield created False and update
    row2 = _mk_row(title="Updated Title", organizers="Org A")
    _wire_sheet_rows(gspread_mocks, [row2])

    with patch.object(ss, "save_image") as mock_save_img2:
        res2 = ss.sync_events("sheet", 0, "B2:I2", request_user=fake_request_user)
    assert res2 and res2[0]["created"] is False
    ev2 = res2[0]["event"]
    assert ev2.id == ev1.id
    assert ev2.title == "Updated Title"
    mock_save_img2.assert_called_once()


@pytest.mark.django_db
def test_sync_events_naive_datetime_made_aware_when_USE_TZ_true(
    settings, credentials_file_ok, monkeypatch, gspread_mocks, fake_request_user
):
    # Force USE_TZ=True for this test
    settings.USE_TZ = True
    Place.objects.create(name="The Venue")
    Organizer.objects.create(name="Org A")
    _install_gspread(monkeypatch, gspread_mocks)
    row = _mk_row(date_str="2025-03-10 09:00", organizers="Org A")
    _wire_sheet_rows(gspread_mocks, [row])

    with patch.object(ss, "save_image"):
        res = ss.sync_events("sheet", 0, "B2:I2", request_user=fake_request_user)

    ev = res[0]["event"]
    assert timezone.is_aware(ev.event_date), "Expected timezone-aware datetime when USE_TZ=True"


@pytest.mark.django_db
def test_sync_events_calls_gspread_with_provided_identifiers(
    credentials_file_ok, monkeypatch, gspread_mocks, fake_request_user
):
    gc = _install_gspread(monkeypatch, gspread_mocks)["gc"]
    _wire_sheet_rows(gspread_mocks, [_mk_row(organizers="Org A")])

    # Prepare required data
    Place.objects.create(name="The Venue")
    Organizer.objects.create(name="Org A")

    with patch.object(ss, "save_image"):
        ss.sync_events("sheet-123", 2, "B2:I100", request_user=fake_request_user)

    gc.open_by_key.assert_called_once_with("sheet-123")
    gspread_mocks["spreadsheet"].get_worksheet.assert_called_once_with(2)
    gspread_mocks["sheet"].get.assert_called_once_with("B2:I100")