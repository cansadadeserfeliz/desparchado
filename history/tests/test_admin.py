import pytest
from django.urls import reverse

from ..models import DATETIME_PRECISION_DAY, Event, Group, HistoricalFigure, Post


@pytest.mark.django_db
def test_show_events_list(django_app, user_admin, history_event):
    response = django_app.get(
        reverse('admin:history_event_changelist'), user=user_admin, status=200,
    )
    assert history_event.title in response


@pytest.mark.django_db
def test_add_event(django_app, user_admin):
    events_count = Event.objects.count()

    response = django_app.get(
        reverse('admin:history_event_add'), user=user_admin, status=200,
    )
    form = response.forms['event_form']
    form['title'] = 'Batalla de Boyacá'
    form['description'] = (
        'La batalla del Puente de Boyacá fue la confrontación más importante '
        'de la guerra de independencia de Colombia que garantizó el éxito '
        'de la Campaña Libertadora de Nueva Granada.'
    )
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
        status=200,
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
        status=200,
    )
    assert history_historical_figure.name in response


@pytest.mark.django_db
def test_add_historical_figure(django_app, user_admin):
    historical_figures_count = HistoricalFigure.objects.count()
    response = django_app.get(
        reverse('admin:history_historicalfigure_add'), user=user_admin, status=200,
    )

    form = response.forms['historicalfigure_form']
    form['name'] = 'Simón Bolívar'
    form['full_name'] = 'Simón José Antonio de la Santísima Trinidad Bolívar'
    form['date_of_birth_0'] = '24/07/1783'
    form['date_of_birth_1'] = '00:00'
    form['date_of_birth_precision'] = DATETIME_PRECISION_DAY
    response = form.submit()

    assert response.status_code == 302
    assert HistoricalFigure.objects.count() == historical_figures_count + 1
    figure = HistoricalFigure.objects.first()
    assert figure.created_by == user_admin


@pytest.mark.django_db
def test_edit_historical_figure(django_app, user_admin, history_historical_figure):
    assert history_historical_figure.created_by != user_admin
    history_historical_figure_creator = history_historical_figure.created_by

    response = django_app.get(
        reverse(
            'admin:history_historicalfigure_change',
            args=(history_historical_figure.id,),
        ),
        user=user_admin,
        status=200,
    )
    form = response.forms['historicalfigure_form']
    response = form.submit()

    assert response.status_code == 302
    history_historical_figure.refresh_from_db()
    assert history_historical_figure.created_by == history_historical_figure_creator


@pytest.mark.django_db
def test_show_post_list(django_app, user_admin, history_post):
    response = django_app.get(
        reverse('admin:history_post_changelist'), user=user_admin, status=200,
    )
    assert str(history_post.historical_figure) in response


@pytest.mark.django_db
def test_add_post(django_app, user_admin):
    posts_count = Post.objects.count()
    response = django_app.get(
        reverse('admin:history_post_add'), user=user_admin, status=200,
    )

    form = response.forms['post_form']
    form['text'] = (
        'Más cuesta mantener el equilibrio de la libertad'
        'que soportar el peso de la tiranía'
    )
    form['post_date_0'] = '24/07/1783'
    form['post_date_1'] = '00:00'
    response = form.submit()

    assert response.status_code == 302
    assert Post.objects.count() == posts_count + 1
    post_instance = Post.objects.first()
    assert post_instance.created_by == user_admin


@pytest.mark.django_db
def test_edit_post(django_app, user_admin, history_post):
    assert history_post.created_by != user_admin
    history_post_creator = history_post.created_by

    response = django_app.get(
        reverse('admin:history_post_change', args=(history_post.id,)),
        user=user_admin,
        status=200,
    )
    form = response.forms['post_form']
    response = form.submit()

    assert response.status_code == 302
    history_post.refresh_from_db()
    assert history_post.created_by == history_post_creator


@pytest.mark.django_db
def test_show_group_list(django_app, user_admin, history_group):
    response = django_app.get(
        reverse('admin:history_group_changelist'), user=user_admin, status=200,
    )
    assert history_group.title in response


@pytest.mark.django_db
def test_add_group(django_app, user_admin):
    groups_count = Group.objects.count()

    response = django_app.get(
        reverse('admin:history_group_add'), user=user_admin, status=200,
    )
    form = response.forms['group_form']
    form['title'] = 'Naturaleza'
    form['description'] = (
        'La batalla del Puente de Boyacá fue la confrontación más importante '
        'de la guerra de independencia de Colombia que garantizó el éxito '
        'de la Campaña Libertadora de Nueva Granada.'
    )
    response = form.submit()
    assert response.status_code == 302

    assert Group.objects.count() == groups_count + 1
    group = Group.objects.get(title='Naturaleza')
    assert group.created_by == user_admin

    assert reverse('admin:history_group_changelist') in response.location


@pytest.mark.django_db
def test_edit_group(django_app, user_admin, history_group):
    assert history_group.created_by != user_admin
    history_group_creator = history_group.created_by

    response = django_app.get(
        reverse('admin:history_group_change', args=(history_group.id,)),
        user=user_admin,
        status=200,
    )
    form = response.forms['group_form']
    response = form.submit()

    assert response.status_code == 302
    history_group.refresh_from_db()
    assert history_group.created_by == history_group_creator
