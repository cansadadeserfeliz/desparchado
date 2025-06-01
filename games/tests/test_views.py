import pytest
from django.urls import reverse

from ..models import HuntingOfSnarkGame


@pytest.mark.django_db
def test_show_main_page_and_create_new_game(
    django_app, hunting_of_snark_criteria_batch
):
    games_count = HuntingOfSnarkGame.objects.count()

    response = django_app.get(reverse('games:hunting_of_snark_create'), status=200)

    player_name = 'Pepito'
    total_points = 10

    form = response.forms['game_form']
    form['player_name'] = player_name
    form['total_points'] = total_points
    response = form.submit().follow()

    assert response.status_code == 200
    assert HuntingOfSnarkGame.objects.count() == games_count + 1

    game = HuntingOfSnarkGame.objects.get(player_name=player_name)
    assert game.total_points == total_points
    assert game.criteria.count() == total_points

    assert response.context['game'] == game
    assert player_name in response


@pytest.mark.django_db
def test_show_criteria_list(django_app, hunting_of_snark_criteria_batch):
    django_app.get(reverse('games:hunting_of_snark_criteria_list'), status=200)


@pytest.mark.django_db
def test_show_games_list(django_app, hunting_of_snark_game):
    response = django_app.get(
        reverse('games:games:hunting_of_snark_games_list'), status=200
    )
    assert hunting_of_snark_game.token in response


@pytest.mark.django_db
def test_show_games_detail(django_app, hunting_of_snark_game):
    django_app.get(
        reverse('games:hunting_of_snark_detail', args=[hunting_of_snark_game.token]),
        status=200,
    )


def test_show_games_list(django_app):
    django_app.get(reverse('games:hunting_of_snark_bbc_top_100'), status=200)
