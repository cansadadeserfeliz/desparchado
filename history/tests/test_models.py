import datetime

import pytest

from ..models import (
    DATETIME_PRECISION_DAY,
    DATETIME_PRECISION_HOUR,
    DATETIME_PRECISION_MINUTE,
    DATETIME_PRECISION_MONTH,
    DATETIME_PRECISION_YEAR,
    get_historical_date_display,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'precision,expected_value',
    [
        (DATETIME_PRECISION_YEAR, '1803'),
        (DATETIME_PRECISION_MONTH, 'abril 1803'),
        (DATETIME_PRECISION_DAY, '5 de abril 1803'),
        (DATETIME_PRECISION_HOUR, '5 de abril 1803, 3 p.m.'),
        (DATETIME_PRECISION_MINUTE, '5 de abril 1803, 3:34 p.m.'),
    ],
)
def test_get_historical_date_display(precision, expected_value):
    historical_date = datetime.datetime(year=1803, month=4, day=5, hour=15, minute=34)
    assert get_historical_date_display(historical_date, precision) == expected_value


@pytest.mark.django_db
@pytest.mark.parametrize(
    'precision,expected_value',
    [
        (DATETIME_PRECISION_YEAR, '-'),
        (DATETIME_PRECISION_MONTH, 'abr'),
        (DATETIME_PRECISION_DAY, '5 abr'),
        (DATETIME_PRECISION_HOUR, '5 abr'),
        (DATETIME_PRECISION_MINUTE, '5 abr'),
    ],
)
def test_get_event_day_and_month_display(precision, expected_value, history_event):
    history_event.event_date = datetime.datetime(
        year=1803, month=4, day=5, hour=15, minute=34,
    )
    history_event.event_date_precision = precision
    history_event.save()
    assert history_event.get_event_day_and_month_display() == expected_value
