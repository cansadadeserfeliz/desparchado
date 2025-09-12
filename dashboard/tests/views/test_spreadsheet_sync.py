from django.urls import reverse

from events.models import Event
from places.tests.factories import PlaceFactory
from events.tests.factories import OrganizerFactory

VIEW_NAME = 'dashboard:spreadsheet_sync_form'


def test_successfully_create_event_with_source_id(django_app, admin_user, mocker, special):
    initial_event_count = Event.objects.count()
    place = PlaceFactory(name='Gran Salón D | Corferias')
    organizer = OrganizerFactory(name='FILBo')

    # fake rows
    fake_rows = [[
        "FILBO2025_142381",
        "Lanzamiento del libro",
        "2025-09-12 15:30",
        place.name,
        "literature",
        "Se realizará la presentación de la novela El incendio de abril",
        "https://example.com/eventos/142381/",
        "",
        organizer.name,
    ]]

    # mock gspread chain
    mock_sheet = mocker.Mock()
    mock_sheet.get.return_value = fake_rows

    mock_spreadsheet = mocker.Mock()
    mock_spreadsheet.get_worksheet.return_value = mock_sheet

    mock_gc = mocker.Mock()
    mock_gc.open_by_key.return_value = mock_spreadsheet

    mocker.patch(
        'dashboard.services.spreadsheet_sync.gspread.service_account_from_dict',
        return_value=mock_gc,
    )

    response = django_app.get(reverse(VIEW_NAME), user=admin_user, status=200)
    form = response.forms["spreadsheet_sync_form"]

    form['spreadsheet_id'] = '1A7_fmZS1QuCt4s9SEVr2D1tq3rRaQjiVNI8vIGBhFEI'
    form['worksheet_number'] = 0
    form['worksheet_range'] = 'A2:L10'
    form['event_id_field'] = 'source_id'
    form['special'].force_value(special.id)
    form['is_hidden'] = True

    response = form.submit()
    assert response.status_code == 200

    assert 'synced_events_data' in response.context
    assert len(response.context['synced_events_data']) == 1, \
        'one event should be synced'
    assert 'errors' not in response.context['synced_events_data'][0]
    assert 'event' in response.context['synced_events_data'][0]

    assert Event.objects.count() == initial_event_count + 1
    event = Event.objects.order_by('-id')[0]

    assert event.source_id == 'FILBO2025_142381'
    assert event.place == place
