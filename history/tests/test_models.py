import pytz
import pytest
import datetime
from django.utils import timezone
from django.conf import settings

from ..models import get_historical_date_display
from ..models import DATETIME_PRECISION_DAY
from ..models import DATETIME_PRECISION_YEAR
from ..models import DATETIME_PRECISION_MONTH
from ..models import DATETIME_PRECISION_HOUR
from ..models import DATETIME_PRECISION_MINUTE


@pytest.mark.django_db
def test_get_historical_date_display():
    historical_date = datetime.datetime(year=1803, month=4, day=5, hour=15, minute=34)
    #historical_date = timezone.localtime(historical_date, timezone=pytz.timezone(settings.TIME_ZONE))

    assert get_historical_date_display(historical_date, DATETIME_PRECISION_YEAR) == '1803'
    assert get_historical_date_display(historical_date, DATETIME_PRECISION_MONTH) == 'abril 1803'
    assert get_historical_date_display(historical_date, DATETIME_PRECISION_DAY) == '5 de abril 1803'
    assert get_historical_date_display(historical_date, DATETIME_PRECISION_HOUR) == '5 de abril 1803, 3 p.m.'
    assert get_historical_date_display(historical_date, DATETIME_PRECISION_MINUTE) == '5 de abril 1803, 3:34 p.m.'
