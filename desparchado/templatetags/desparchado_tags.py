import calendar
from urllib.parse import urlparse

from django import template

from desparchado.utils import get_natural_day

register = template.Library()


# Perform the comparison in the default time zone when USE_TZ = True
# (unless a specific time zone has been applied with the |timezone filter).
@register.filter(expects_localtime=True)
def natural_day_no_default(value):
    """
    For date values that are tomorrow, today or yesterday compared to
    present day return representing string.
    Otherwise, return an empty string.

    See from django.contrib.humanize.templatetags.humanize.naturalday
    """
    return get_natural_day(value)


@register.filter(expects_localtime=True)
def natural_day(value):
    """
    For date values that are tomorrow, today or yesterday compared to
    present day return representing string.
    Otherwise, return the original date.

    See from django.contrib.humanize.templatetags.humanize.naturalday
    """
    return get_natural_day(value) or value


@register.filter()
def format_currency(value):
    """
    E.g. 543921.9354 becomes $543,921.94
    """
    try:
        value = float(value)
        return f'${value:,.0f}'
    except (ValueError, TypeError):
        return value


@register.filter()
def weekday_to_str(weekday_number):
    return calendar.day_name[int(weekday_number) - 1]


@register.filter()
def shorten_url(value):
    """
    E.g. 543921.9354 becomes $543,921.94
    """
    parsed_uri = urlparse(value)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain


@register.filter()
def user_can_edit_event(user, event):
    if user.is_authenticated:
        return event.can_edit(user)
    return False


@register.filter()
def user_can_edit_organizer(user, organizer):
    if user.is_authenticated:
        return organizer.can_edit(user)
    return False


@register.filter()
def user_can_edit_speaker(user, speaker):
    if user.is_authenticated:
        return speaker.can_edit(user)
    return False


@register.filter()
def user_can_edit_place(user, place):
    if user.is_authenticated:
        return place.can_edit(user)
    return False

@register.filter()
def group_events(events, n=3):
    """
    Groups list into chunks of size n.
    Keeps the last chunk even if it has fewer items.
    """
    return [events[i:i+n] for i in range(0, len(events), n)]
