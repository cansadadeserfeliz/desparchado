import calendar
import logging
from datetime import date, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext
from html_sanitizer import Sanitizer

logger = logging.getLogger(__name__)
sanitizer = Sanitizer(
    {
        'keep_typographic_whitespace': True,
    },
)


def get_natural_day(target: date):
    """
    Converts a date to a natural language description relative to today.

    Args:
        target: A date object to convert to natural language
    Returns:
        A localized string describing the date (today, tomorrow, yesterday,
        this week, next week, this month, next month) or an empty string
        if none of these categories apply. Returns the input unchanged if
        it's not a date object.
    """
    try:
        target = date(target.year, target.month, target.day)
    except AttributeError:
        # Passed target wasn't a date object
        return target

    today = timezone.now().date()
    delta = target - today

    if delta.days == 0:
        return gettext('hoy')

    if delta.days == 1:
        return gettext('mañana')

    if delta.days == -1:
        return gettext('ayer')

    # Extract this to reduce complexity
    return _get_relative_timeframe(target, today)


def _get_relative_timeframe(target: date, today: date):
    """Helper function to determine relative timeframe of a date."""

    # Week boundaries
    # Assuming weeks start on Monday (0) and end on Sunday (6)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    start_of_next_week = end_of_week + timedelta(days=1)
    end_of_next_week = start_of_next_week + timedelta(days=6)

    if start_of_week <= target <= end_of_week:
        return gettext('esta semana')

    if start_of_next_week <= target <= end_of_next_week:
        return gettext('próxima semana')

    # This month
    _, days_in_month = calendar.monthrange(today.year, today.month)
    end_of_month = date(today.year, today.month, days_in_month)
    if today <= target <= end_of_month:
        return gettext('este mes')

    # Next month
    next_month_year = today.year + (today.month // 12)
    next_month = (today.month % 12) + 1
    _, days_in_next_month = calendar.monthrange(next_month_year, next_month)
    start_of_next_month = date(next_month_year, next_month, 1)
    end_of_next_month = date(next_month_year, next_month, days_in_next_month)

    if start_of_next_month <= target <= end_of_next_month:
        return gettext('próximo mes')

    return ''


def send_admin_notification(request, obj, form, change):
    """
    Sends an email notification to admin users when an object is created or updated.

    The email subject indicates whether the object was created or updated,
    includes the model name, object, and user, and the body contains a link
    to the object's detail page.
    """
    try:
        purpose = 'Updated' if change else 'Created new'
        model = form.Meta.model._meta.model_name
        send_mail(
            f'{purpose} {model} "{obj}" by {request.user}',
            f'https://desparchado.co{obj.get_absolute_url()}',
            settings.EMAIL_FROM,
            settings.EMAIL_ADMIN_USERS,
            fail_silently=True,
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error('No se pudo enviar correo electrónico', exc_info=e)


def send_notification(request, obj, model_name, created):
    """
    Sends an email notification about the creation or update of an object,
    unless the user is a superuser.

    Args:
        request: The HTTP request containing the user performing the action.
        obj: The object that was created or updated.
        model_name: The name of the object's model.
        created: Boolean indicating if the object was created (True) or updated (False).
    """
    if request.user.is_superuser:
        return

    try:
        purpose = 'Created new' if created else 'Updated'
        send_mail(
            f'{purpose} {model_name} "{obj}" by {request.user}',
            f'https://desparchado.co{obj.get_absolute_url()}',
            settings.EMAIL_FROM,
            settings.EMAIL_ADMIN_USERS,
            fail_silently=True,
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.exception('No se pudo enviar correo electrónico', exc_info=e)


def sanitize_html(html: str):
    """
    Sanitizes an HTML string by removing or altering potentially unsafe content.

    Args:
        html: The HTML string to sanitize.

    Returns:
        The sanitized HTML string with typographic whitespace preserved.
    """
    return sanitizer.sanitize(html)
