import pytest

from django.urls import reverse

from ..models import Event, HistoricalFigure
from ..models import DATETIME_PRECISION_DAY


@pytest.mark.django_db
def test_show_events_list(django_app, user_admin, history_event):
    response = django_app.get(
        reverse('admin:history_event_changelist'),
        user=user_admin,
        status=200
    )
    assert history_event.title in response


@pytest.mark.django_db
def test_add_event(django_app, user_admin):
    events_count = Event.objects.count()

    response = django_app.get(
        reverse('admin:history_event_add'),
        user=user_admin,
        status=200
    )
    form = response.forms['event_form']
    form['title'] = 'Batalla de Boyacá'
    form['description'] = 'La batalla del Puente de Boyacá fue la confrontación más importante de la guerra ' \
                          'de independencia de Colombia que garantizó el éxito de la Campaña Libertadora ' \
                          'de Nueva Granada.'
    form['event_date_0'] = '07/08/1819'
    form['event_date_1'] = '00:00'
    form['event_date_precision'] = DATETIME_PRECISION_DAY
    response = form.submit()
    assert response.status_code == 302

    assert Event.objects.count() == events_count + 1
    event = Event.objects.first()
    assert event.created_by == user_admin

    assert reverse('admin:history_event_changelist') in response.location


@pytest.mark.django_db
def test_edit_event(django_app, user_admin, history_event):
    assert history_event.created_by != user_admin
    history_event_creator = history_event.created_by

    response = django_app.get(
        reverse('admin:history_event_change', args=(history_event.id,)),
        user=user_admin,
        status=200
    )
    form = response.forms['event_form']
    response = form.submit()

    assert response.status_code == 302
    history_event.refresh_from_db()
    assert history_event.created_by == history_event_creator


@pytest.mark.django_db
def test_show_historical_figure_list(django_app, user_admin, history_historical_figure):
    response = django_app.get(
        reverse('admin:history_historicalfigure_changelist'),
        user=user_admin,
        status=200
    )
    assert history_historical_figure.name in response

