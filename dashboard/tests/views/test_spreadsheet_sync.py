import io

import pytest
from django.urls import reverse

from dashboard.models import SpreadsheetSync
from dashboard.tests.factories import SpreadsheetSyncFactory
from events.models import Event
from events.tests.factories import EventFactory, OrganizerFactory
from places.tests.factories import PlaceFactory

VIEW_NAME = 'dashboard:spreadsheet_sync_form'


def _get_mock_gc(mocker, fake_rows: list[list]):
    mocker.patch(
        "dashboard.services.spreadsheet_sync.Path.open",
        return_value=io.StringIO(
            '{"type":"service_account","client_email":"x","private_key":"y"}',
        ),
    )

    # mock gspread chain
    mock_sheet = mocker.Mock()
    mock_sheet.get.return_value = fake_rows

    mock_spreadsheet = mocker.Mock()
    mock_spreadsheet.get_worksheet.return_value = mock_sheet

    mock_gc = mocker.Mock()
    mock_gc.open_by_key.return_value = mock_spreadsheet

    return mock_gc


def _get_valid_row(place, organizers):
    return [
        "FILBO2025_142381",
        "Lanzamiento del libro",
        "2025-09-12 15:30",
        place.name,
        "literature",
        "Se realizará la presentación de la novela El incendio de abril",
        "https://example.com/eventos/142381/",
        "",
        ', '.join([organizer.name for organizer in organizers]),
    ]


@pytest.mark.django_db
def test_successfully_create_event_with_source_id(
    django_app, admin_user, mocker,
):
    initial_event_count = Event.objects.count()
    place = PlaceFactory(name='Gran Salón D | Corferias')
    organizer = OrganizerFactory(name='FILBo')
    row = _get_valid_row(place=place, organizers=[organizer])

    mocker.patch(
        'dashboard.services.spreadsheet_sync.gspread.service_account_from_dict',
        return_value=_get_mock_gc(mocker, [row]),
    )

    response = django_app.get(reverse(VIEW_NAME), user=admin_user, status=200)
    form = response.forms["spreadsheet_sync_form"]

    spreadsheet_sync = SpreadsheetSyncFactory(
        event_id_field=SpreadsheetSync.EventIdField.SOURCE_ID,
        is_hidden=True,
    )
    form["spreadsheet_sync"].force_value(spreadsheet_sync.id)
    form["worksheet_range"] = "A2:L10"

    response = form.submit()
    assert response.status_code == 200

    assert 'synced_events_data' in response.context
    assert len(response.context['synced_events_data']) == 1, \
        'one event should be synced'
    assert response.context['synced_events_data'][0].error == ''
    assert response.context['synced_events_data'][0].event is not None
    assert response.context['synced_events_data'][0].created is True

    assert Event.objects.count() == initial_event_count + 1
    event = Event.objects.order_by('-id')[0]

    assert event.source_id == row[0]
    assert event.title == row[1]
    assert event.place == place
    assert organizer in event.organizers.all()
    assert spreadsheet_sync.special.related_events.filter(pk=event.pk).exists()
    assert event.is_hidden == spreadsheet_sync.is_hidden
    assert event.created_by == admin_user


@pytest.mark.django_db
def test_successfully_update_event_with_source_id(django_app, admin_user, mocker):
    place = PlaceFactory(name='Gran Salón D | Corferias')
    organizer = OrganizerFactory(name='FILBo')
    row = _get_valid_row(place=place, organizers=[organizer])

    event = EventFactory(source_id=row[0])

    initial_event_count = Event.objects.count()

    fake_rows = [row]
    mocker.patch(
        'dashboard.services.spreadsheet_sync.gspread.service_account_from_dict',
        return_value=_get_mock_gc(mocker, fake_rows),
    )

    response = django_app.get(reverse(VIEW_NAME), user=admin_user, status=200)
    form = response.forms['spreadsheet_sync_form']

    spreadsheet_sync = SpreadsheetSyncFactory(
        event_id_field=SpreadsheetSync.EventIdField.SOURCE_ID,
        is_hidden=True,
    )
    form["spreadsheet_sync"].force_value(spreadsheet_sync.id)
    form["worksheet_range"] = "A2:L10"

    response = form.submit()
    assert response.status_code == 200

    assert 'synced_events_data' in response.context
    assert len(response.context['synced_events_data']) == 1, \
        'one event should be synced'
    assert response.context['synced_events_data'][0].error == ''
    assert response.context['synced_events_data'][0].event is not None
    assert response.context["synced_events_data"][0].created is False

    assert Event.objects.count() == initial_event_count
    event.refresh_from_db()

    assert event.source_id == row[0]
    assert event.title == row[1]
    assert event.place == place
    assert organizer in event.organizers.all()
    assert spreadsheet_sync.special.related_events.filter(pk=event.pk).exists()
    assert event.is_hidden == spreadsheet_sync.is_hidden


@pytest.mark.django_db
def test_successfully_update_event_with_event_source_url(
    django_app, admin_user, mocker,
):
    place = PlaceFactory(name='Gran Salón D | Corferias')
    organizer = OrganizerFactory(name='FILBo')
    row = _get_valid_row(place=place, organizers=[organizer])
    row[0] = ''

    event = EventFactory(event_source_url=row[6])

    initial_event_count = Event.objects.count()

    fake_rows = [row]
    mocker.patch(
        'dashboard.services.spreadsheet_sync.gspread.service_account_from_dict',
        return_value=_get_mock_gc(mocker, fake_rows),
    )

    response = django_app.get(reverse(VIEW_NAME), user=admin_user, status=200)
    form = response.forms['spreadsheet_sync_form']

    spreadsheet_sync = SpreadsheetSyncFactory(
        event_id_field=SpreadsheetSync.EventIdField.EVENT_SOURCE_URL,
        is_hidden=True,
    )
    form["spreadsheet_sync"].force_value(spreadsheet_sync.id)
    form["worksheet_range"] = "A2:L10"

    response = form.submit()
    assert response.status_code == 200

    assert 'synced_events_data' in response.context
    assert len(response.context['synced_events_data']) == 1, \
        'one event should be synced'
    assert response.context['synced_events_data'][0].error == ''
    assert response.context['synced_events_data'][0].event is not None

    assert Event.objects.count() == initial_event_count
    event.refresh_from_db()

    assert event.source_id is None, 'source_id was not set'
    assert event.title == row[1]
    assert event.place == place
    assert organizer in event.organizers.all()
    assert spreadsheet_sync.special.related_events.filter(pk=event.pk).exists()
    assert event.is_hidden is True


@pytest.mark.django_db
@pytest.mark.parametrize(
    'column_index,value,error_message',
    [
        [0, '', 'source_id is empty'],
        [1, '', 'Title is empty'],
        [2, 'invalid_date', 'Invalid event_date: "invalid_date"'],
        [3, 'invalid_place', 'Place "invalid_place" not found'],
        [4, 'invalid_category', 'Invalid category: "invalid_category"'],
        [5, '', 'Description is empty'],
        [6, '', 'Empty event_source_url'],
        [6, 'X'*501, 'event_source_url exceeds maximum length (501>500)'],
    ],
)
def test_validation(
    django_app, admin_user, place, organizer, mocker,
    column_index, value, error_message,
):
    initial_event_count = Event.objects.count()

    row = _get_valid_row(place=place, organizers=[organizer])
    row[column_index] = value
    fake_rows = [row]
    mocker.patch(
        'dashboard.services.spreadsheet_sync.gspread.service_account_from_dict',
        return_value=_get_mock_gc(mocker, fake_rows),
    )

    response = django_app.get(reverse(VIEW_NAME), user=admin_user, status=200)
    form = response.forms["spreadsheet_sync_form"]

    spreadsheet_sync = SpreadsheetSyncFactory(
        event_id_field=SpreadsheetSync.EventIdField.SOURCE_ID,
    )
    form["spreadsheet_sync"].force_value(spreadsheet_sync.id)
    form["worksheet_range"] = "A2:L10"

    response = form.submit()
    assert response.status_code == 200

    assert Event.objects.count() == initial_event_count, 'no new events created'

    assert 'synced_events_data' in response.context
    assert len(response.context['synced_events_data']) == 1, \
        'one row has an error'
    assert response.context['synced_events_data'][0].event is None
    assert response.context['synced_events_data'][0].error == error_message


@pytest.mark.django_db
def test_successfully_create_event_with_non_existing_organizer(
        django_app, admin_user, mocker,
):
    initial_event_count = Event.objects.count()
    place = PlaceFactory(name='Gran Salón D | Corferias')
    organizer_1 = OrganizerFactory(name='FILBo')
    organizer_2 = OrganizerFactory(name='Idartes')
    row = _get_valid_row(place=place, organizers=[organizer_1, organizer_2])
    organizer_2.delete()

    mocker.patch(
        'dashboard.services.spreadsheet_sync.gspread.service_account_from_dict',
        return_value=_get_mock_gc(mocker, [row]),
    )

    response = django_app.get(reverse(VIEW_NAME), user=admin_user, status=200)
    form = response.forms["spreadsheet_sync_form"]

    spreadsheet_sync = SpreadsheetSyncFactory(
        event_id_field=SpreadsheetSync.EventIdField.SOURCE_ID,
    )
    form["spreadsheet_sync"].force_value(spreadsheet_sync.id)
    form["worksheet_range"] = "A2:L10"

    response = form.submit()
    assert response.status_code == 200

    assert 'synced_events_data' in response.context
    assert len(response.context['synced_events_data']) == 1, \
        'one event should be synced'
    assert response.context['synced_events_data'][0].error == ''
    assert response.context['synced_events_data'][0].event is not None
    assert ('Organizer "Idartes" not found' in
            response.context['synced_events_data'][0].warnings)

    assert Event.objects.count() == initial_event_count + 1
