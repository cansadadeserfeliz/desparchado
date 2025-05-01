from datetime import date, datetime
from urllib.parse import urlparse

import calendar
import markdown

from django import template
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

register = template.Library()


# Perform the comparison in the default time zone when USE_TZ = True
# (unless a specific time zone has been applied with the |timezone filter).
@register.filter(expects_localtime=True)
@register.filter
def naturalday_no_default(value, arg=None):
    """
    For date values that are tomorrow, today or yesterday compared to
    present day return representing string.
    Otherwise, return an empty string.

    See from django.contrib.humanize.templatetags.humanize.naturalday
    """
    tzinfo = getattr(value, "tzinfo", None)
    try:
        value = date(value.year, value.month, value.day)
    except AttributeError:
        # Passed value wasn't a date object
        return value
    today = datetime.now(tzinfo).date()
    delta = value - today
    if delta.days == 0:
        return _("today")
    elif delta.days == 1:
        return _("tomorrow")
    elif delta.days == -1:
        return _("yesterday")
    return ''

@register.filter()
def format_currency(value):
    """
    E.g. 543921.9354 becomes $543,921.94
    """
    try:
        value = float(value)
        return '${:,.0f}'.format(value)
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


@register.filter(name='markdown')
def markdown_filter(text):
    return mark_safe(markdown.markdown(text))
