from urllib.parse import urlparse
import calendar

import markdown

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


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
