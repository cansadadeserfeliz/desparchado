from django.urls import reverse

from django_webtest import WebTest

from ..models import HuntingOfSnarkGame
from .factories import HuntingOfSnarkCriteriaFactory
from .factories import HuntingOfSnarkGameFactory


class HuntingOfSnarkGameTest(WebTest):

    def setUp(self):
        HuntingOfSnarkCriteriaFactory.create_batch(50)
        self.game = HuntingOfSnarkGameFactory()

    def test_show_main_page_and_create_new_game(self):
        self.assertEqual(HuntingOfSnarkGame.objects.count(), 1)
        response = self.app.get(reverse('games:hunting_of_snark_create'), status=200)

        player_name = 'Pepito'
        total_points = 10

        form = response.forms['game_form']
        form['player_name'] = player_name
        form['total_points'] = total_points
        response = form.submit().follow()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(HuntingOfSnarkGame.objects.count(), 2)

        game = HuntingOfSnarkGame.objects.filter(player_name=player_name).first()
        self.assertEqual(game.total_points, total_points)
        self.assertEqual(game.total_points, total_points)
        self.assertEqual(game.criteria.count(), total_points)

        self.assertEqual(response.context['game'], game)
        self.assertContains(response, player_name)

    def test_show_criteria_list(self):
        self.app.get(
            reverse('games:hunting_of_snark_criteria_list'),
            status=200
        )

    def test_show_games_list(self):
        self.app.get(
            reverse('games:hunting_of_snark_games_list'),
            status=200
        )

    def test_show_bbc_top_100(self):
        self.app.get(
            reverse('games:hunting_of_snark_bbc_top_100'),
            status=200
        )

    def test_show_bbc_top_100(self):
        self.app.get(
            reverse('games:hunting_of_snark_detail', args=[self.game.token]),
            status=200
        )
