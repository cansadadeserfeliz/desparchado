import builtins
import io
import json
from types import SimpleNamespace
from datetime import datetime, timezone as dt_timezone

import pytest

# Framework note:
# These tests are written for pytest (with pytest-django if Django is present).
# We mock Django ORM interactions and external services (gspread, requests)
# to isolate pure logic.

# Target module under test
# The implementation appears under dashboard/tests/test_services_spreadsheet_sync.py per PR context.
# Import it with an alias to avoid collision with this test module name.
import importlib.util
from pathlib import Path

_IMPL_PATH = Path("dashboard/tests/test_services_spreadsheet_sync.py")

spec = importlib.util.spec_from_file_location("services_spreadsheet_sync_impl", _IMPL_PATH)
impl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(impl)

# Utilities for building mocks

class DummyImageField:
    def __init__(self):
        self.saved = []

    def save(self, filename, content_file, save=True):
        # Record calls for assertion
        # content_file is a Django ContentFile; we just store its len for validation
        data = getattr(content_file, "read", None)
        if callable(data):
            payload = content_file.read()
        else:
            payload = getattr(content_file, "content", b"")
        self.saved.append((filename, len(payload), save))


class DummyEvent:
    def __init__(self, slug="my-event-slug"):
        self.slug = slug
        self.image = DummyImageField()
        self.organizers_set_calls = []

    @property
    def organizers(self):
        class _Mgr:
            def __init__(self, outer):
                self.outer = outer

            def set(self, objs):
                self.outer.organizers_set_calls.append(list(objs))
        return _Mgr(self)


@pytest.fixture(autouse=True)
def _isolate_settings(monkeypatch, tmp_path):
    # Provide minimal settings used by the implementation
    class Settings:
        BASE_DIR = tmp_path
        USE_TZ = True
    monkeypatch.setattr(impl, "settings", Settings, raising=True)
    # Provide predictable timezone behavior
    class _TZ:
        @staticmethod
        def is_naive(dt):
            return dt.tzinfo is None

        @staticmethod
        def make_aware(dt, tz):
            return dt.replace(tzinfo=dt_timezone.utc)

        @staticmethod
        def get_current_timezone():
            return dt_timezone.utc
    monkeypatch.setattr(impl, "timezone", _TZ, raising=True)


@pytest.fixture
def credentials_file(tmp_path, monkeypatch):
    data = {"type": "service_account", "project_id": "proj"}
    cred_path = tmp_path / "spreadsheet_credentials.json"
    cred_path.write_text(json.dumps(data), encoding="utf-8")
    return data


@pytest.fixture
def mock_gspread(monkeypatch):
    class _Sheet:
        def __init__(self, rows):
            self._rows = rows
        def get(self, rng):
            return list(self._rows)

    class _Spreadsheet:
        def __init__(self, sheet):
            self._sheet = sheet
        def get_worksheet(self, idx):
            return self._sheet

    class _GC:
        def __init__(self, spreadsheet):
            self._spreadsheet = spreadsheet
        def open_by_key(self, key):
            return self._spreadsheet

    state = {}
    def _svc_from_dict(d):
        return _GC(state["spreadsheet"])
    monkeypatch.setattr(impl.gspread, "service_account_from_dict", _svc_from_dict, raising=True)
    return state


@pytest.fixture
def mock_models(monkeypatch):
    # Mock Place, Organizer, Event ORM behaviors
    class _DoesNotExist(Exception): ...
    class Place:
        DoesNotExist = _DoesNotExist
        _by_name = {}
        @classmethod
        def objects(cls):
            return cls
        @classmethod
        def get(cls, **kwargs):
            name = kwargs.get("name__iexact")
            if name and name.lower() in cls._by_name:
                return cls._by_name[name.lower()]
            raise cls.DoesNotExist()
    class Organizer:
        DoesNotExist = _DoesNotExist
        _by_name = {}
        @classmethod
        def objects(cls):
            return cls
        @classmethod
        def get(cls, **kwargs):
            name = kwargs.get("name__iexact")
            if name and name.lower() in cls._by_name:
                return cls._by_name[name.lower()]
            raise cls.DoesNotExist()
    class EventMgr:
        def __init__(self):
            self.calls = []
        def update_or_create(self, **kwargs):
            # Implementation expects 'create_defaults' (nonstandard).
            create_defaults = kwargs.pop("create_defaults", None)
            defaults = kwargs.pop("defaults", None)
            self.calls.append(dict(lookup=kwargs, defaults=defaults, create_defaults=create_defaults))
            ev = DummyEvent(slug="synced-event")
            # Created True if an explicit flag in lookup is new, otherwise False
            return ev, True
    class Event:
        objects = EventMgr()

    monkeypatch.setattr(impl, "Place", Place, raising=True)
    monkeypatch.setattr(impl, "Organizer", Organizer, raising=True)
    monkeypatch.setattr(impl, "Event", Event, raising=True)
    return dict(Place=Place, Organizer=Organizer, Event=Event)


@pytest.fixture
def mock_sanitize(monkeypatch):
    def _sanitize(html):
        return f"[sanitized]{html}"
    monkeypatch.setattr(impl, "sanitize_html", _sanitize, raising=True)


def test_get_cell_data_happy_path():
    row = ["id", "  Title  ", "2025-01-02", "Place", "Cat", " <p>desc</p> ", "url", "", "Org A, Org B"]
    assert impl._get_cell_data(row, "B") == "Title"
    assert impl._get_cell_data(row, "F") == "<p>desc</p>"


def test_get_cell_data_out_of_range_returns_empty():
    row = ["A"]
    assert impl._get_cell_data(row, "C") == ""


def test_sync_events_returns_error_if_credentials_missing(tmp_path, monkeypatch):
    # No credentials file written
    # Ensure logs don't break the test
    result = impl.sync_events(
        spreadsheet_id="abc",
        worksheet_number=0,
        worksheet_range="B2:H10",
        request_user=SimpleNamespace(id=1, username="tester"),
    )
    assert isinstance(result, list) and result
    assert result[0]["error"] == "Spreadsheet credentials could not be loaded"


def test_sync_events_parses_rows_and_creates_events(credentials_file, mock_gspread, mock_models, mock_sanitize, monkeypatch, tmp_path):
    # Prepare credential file
    cred_path = Path(tmp_path) / "spreadsheet_credentials.json"
    cred_path.write_text(json.dumps(credentials_file), encoding="utf-8")

    # Seed Place and Organizer fixtures
    mock_models["Place"]._by_name = {"venue x": SimpleNamespace(id=1, name="Venue X")}
    mock_models["Organizer"]._by_name = {
        "org a": SimpleNamespace(id=10, name="Org A"),
        "org b": SimpleNamespace(id=11, name="Org B"),
    }

    # Prepare sheet rows (B..I columns used)
    # [B title, C date, D place, E category, F desc, G source, H image, I organizers]
    rows = [
        ["My Title", "2025-02-03 19:30", "Venue X", "music", "<b>hello</b>", "http://src/1", "http://img/1.jpg", "Org A, Org B"],  # valid
    ]
    sheet = type("Sheet", (), {"get": lambda self, r: rows})()
    spreadsheet = type("SS", (), {"get_worksheet": lambda self, i: sheet})()
    mock_gspread["spreadsheet"] = spreadsheet

    # Stub save_image to avoid network
    save_calls = []
    def _save_image(event, url):
        save_calls.append((event.slug, url))
    monkeypatch.setattr(impl, "save_image", _save_image, raising=True)

    user = SimpleNamespace(id=99, username="importer")
    out = impl.sync_events("sheet-key", 0, "B2:I3", user)

    assert len(out) == 1
    item = out[0]
    assert item["created"] is True
    assert item["event"].slug == "synced-event"
    # Verify Event.objects.update_or_create received expected arguments
    call = mock_models["Event"].objects.calls[-1]
    assert call["lookup"] == {"event_source_url": "http://src/1"}
    assert call["defaults"]["title"] == "My Title"
    assert call["defaults"]["category"] == "music"
    assert call["defaults"]["place"].name == "Venue X"
    assert str(call["defaults"]["event_date"].tzinfo) == "UTC"
    assert call["defaults"]["description"] == "[sanitized]<b>hello</b>"
    # organizers set called with Org A and Org B
    assert len(item["event"].organizers_set_calls) == 1
    names = [o.name for o in item["event"].organizers_set_calls[0]]
    assert set(names) == {"Org A", "Org B"}
    # image save called
    assert save_calls == [("synced-event", "http://img/1.jpg")]


def test_sync_events_invalid_date_yields_error(credentials_file, mock_gspread, mock_models, monkeypatch, tmp_path):
    Path(tmp_path, "spreadsheet_credentials.json").write_text(json.dumps(credentials_file), encoding="utf-8")
    rows = [["Title", "not-a-date", "Venue X", "cat", "desc", "src", "", "Org A"]]
    sheet = type("Sheet", (), {"get": lambda self, r: rows})()
    spreadsheet = type("SS", (), {"get_worksheet": lambda self, i: sheet})()
    mock_gspread["spreadsheet"] = spreadsheet

    # Patch dateutil.parse to raise
    def _raise(_):
        raise ValueError("bad date")
    from dateutil import parser as dateutil_parser
    monkeypatch.setattr(impl, "parse", _raise, raising=True)

    out = impl.sync_events("key", 0, "B2:I2", SimpleNamespace())
    assert out and "error" in out[0]
    assert 'Invalid event_date' in out[0]["error"]


def test_sync_events_missing_place_yields_error(credentials_file, mock_gspread, mock_models, monkeypatch, tmp_path):
    Path(tmp_path, "spreadsheet_credentials.json").write_text(json.dumps(credentials_file), encoding="utf-8")
    # Place not seeded => DoesNotExist
    rows = [["Title", "2025-04-05", "Unknown Venue", "cat", "desc", "src", "", ""]]
    sheet = type("Sheet", (), {"get": lambda self, r: rows})()
    spreadsheet = type("SS", (), {"get_worksheet": lambda self, i: sheet})()
    mock_gspread["spreadsheet"] = spreadsheet

    out = impl.sync_events("key", 0, "B2:I2", SimpleNamespace())
    assert out and "error" in out[0]
    assert 'Place "Unknown Venue" not found' == out[0]["error"]


def test_sync_events_organizer_warnings(credentials_file, mock_gspread, mock_models, monkeypatch, tmp_path):
    Path(tmp_path, "spreadsheet_credentials.json").write_text(json.dumps(credentials_file), encoding="utf-8")
    # Seed only Org A, not Org X
    mock_models["Place"].._by_name = {"venue": SimpleNamespace(id=1, name="Venue")}
    mock_models["Organizer"]._by_name = {"org a": SimpleNamespace(id=10, name="Org A")}
    rows = [["Title", "2025-05-06", "Venue", "cat", "desc", "src", "", "Org A, Org X , Org A"]]
    sheet = type("Sheet", (), {"get": lambda self, r: rows})()
    spreadsheet = type("SS", (), {"get_worksheet": lambda self, i: sheet})()
    mock_gspread["spreadsheet"] = spreadsheet

    out = impl.sync_events("key", 0, "B2:I2", SimpleNamespace())
    assert out and "warnings" in out[0]
    assert out[0]["warnings"] == ['Organizer "Org X" not found']
    # organizers set should receive deduped existing organizer once
    ev = out[0]["event"]
    assert len(ev.organizers_set_calls) == 1
    assert [o.name for o in ev.organizers_set_calls[0]] == ["Org A"]


def test_save_image_success(monkeypatch):
    event = DummyEvent(slug="s1")
    # Mock requests.get
    class Resp:
        status_code = 200
        headers = {"Content-Type": "image/png; charset=binary"}
        content = b"\x89PNG..."
    monkeypatch.setattr(impl.requests, "get", lambda url, timeout: Resp(), raising=True)
    # Force known extension
    monkeypatch.setattr(impl.mimetypes, "guess_extension", lambda ct: ".png", raising=True)

    impl.save_image(event, "http://example/image.png")
    assert event.image.saved, "image should be saved"
    filename, size, save_flag = event.image.saved[0]
    assert filename == "s1.png"
    assert size == len(b"\x89PNG...")
    assert save_flag is True


def test_save_image_non_200_skips(monkeypatch):
    event = DummyEvent(slug="s2")
    class Resp:
        status_code = 404
        headers = {"Content-Type": "text/html"}
        content = b"nope"
    monkeypatch.setattr(impl.requests, "get", lambda url, timeout: Resp(), raising=True)

    impl.save_image(event, "http://example/missing.jpg")
    assert event.image.saved == []


def test_save_image_non_image_content_type_skips(monkeypatch):
    event = DummyEvent(slug="s3")
    class Resp:
        status_code = 200
        headers = {"Content-Type": "text/plain"}
        content = b"not an image"
    monkeypatch.setattr(impl.requests, "get", lambda url, timeout: Resp(), raising=True)

    impl.save_image(event, "http://example/file.txt")
    assert event.image.saved == []


def test_save_image_fallback_ext_when_unknown(monkeypatch):
    event = DummyEvent(slug="s4")
    class Resp:
        status_code = 200
        headers = {"Content-Type": "image/unknown"}
        content = b"..."
    monkeypatch.setattr(impl.requests, "get", lambda url, timeout: Resp(), raising=True)
    # Force guess_extension to None -> fallback to .jpg
    monkeypatch.setattr(impl.mimetypes, "guess_extension", lambda ct: None, raising=True)

    impl.save_image(event, "http://example/whatever")
    assert event.image.saved
    assert event.image.saved[0][0] == "s4.jpg"


def test_save_image_request_exception_logged_and_skipped(monkeypatch):
    event = DummyEvent(slug="s5")
    class Boom(Exception): ...
    def _raise(url, timeout):
        raise impl.requests.RequestException("boom")
    monkeypatch.setattr(impl.requests, "get", _raise, raising=True)
    impl.save_image(event, "http://example/x")
    assert event.image.saved == []