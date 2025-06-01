from django.core.management.base import BaseCommand

from history.tests.factories import (
    HistoricalFigureFactory,
    PostFactory,
    EventFactory,
    GroupFactory,
)


class Command(BaseCommand):
    help = "Generate random history data for local environment"

    def handle(self, *args, **options):
        historical_figure_1 = HistoricalFigureFactory(name='Simón Bolívar')
        historical_figure_2 = HistoricalFigureFactory(name='Francisco de Paula Santander')
        historical_figure_3 = HistoricalFigureFactory(name='Manuela Sáenz')

        GroupFactory()
        EventFactory.create_batch(3)

        PostFactory(historical_figure=historical_figure_1)
        PostFactory(historical_figure=historical_figure_2)

        post = PostFactory(historical_figure=historical_figure_3)
        post.historical_figure_mentions.add(historical_figure_1, historical_figure_2)

        self.stdout.write(
            self.style.SUCCESS('Successfully created random history data')
        )
