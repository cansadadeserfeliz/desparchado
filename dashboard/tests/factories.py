import random
import string

import factory
import factory.fuzzy

from specials.tests.factories import SpecialFactory

from ..models import SpreadsheetSync


def random_spreadsheet_id():
    # Google spreadsheet IDs are usually 44 chars of letters, numbers, dashes,
    # underscores
    alphabet = string.ascii_letters + string.digits + '-_'
    return ''.join(random.choice(alphabet) for _ in range(44))


class SpreadsheetSyncFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('name')
    spreadsheet_id = factory.LazyFunction(random_spreadsheet_id)
    event_id_field = SpreadsheetSync.EventIdField.SOURCE_ID
    special = factory.SubFactory(SpecialFactory)

    class Meta:
        model = SpreadsheetSync
