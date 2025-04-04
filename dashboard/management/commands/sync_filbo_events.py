from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from dashboard.services import sync_filbo_events

User = get_user_model()


class Command(BaseCommand):
    help = 'Syncs FILBo events from a spreadsheet'

    def add_arguments(self, parser):
        parser.add_argument('spreadsheet_id', type=str)

    def handle(self, *args, **options):
        spreadsheet_id = options['spreadsheet_id']
        self.stdout.write(
            self.style.NOTICE(f'Started sync for {spreadsheet_id}')
        )

        user = User.objects.get(username='root')

        sync_filbo_events(
            spreadsheet_id=spreadsheet_id,
            worksheet_number=0,
            worksheet_range='A2:L3000',
            request_user=user,
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully synced {spreadsheet_id}')
        )
