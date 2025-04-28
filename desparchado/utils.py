import logging
from html_sanitizer import Sanitizer

from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)
sanitizer = Sanitizer({
    'keep_typographic_whitespace': True,
})


def send_admin_notification(request, obj, form, change):
    """
    Sends an email notification to admin users when an object is created or updated.
    
    The email subject indicates whether the object was created or updated, includes the model name, object, and user, and the body contains a link to the object's detail page.
    """
    try:
        send_mail(
            '{purpose} {model} "{obj}" by {user}'.format(
                purpose='Updated' if change else 'Created new',
                model=form.Meta.model._meta.model_name,
                obj=str(obj),
                user=str(request.user),
            ),
            'https://desparchado.co{}'.format(obj.get_absolute_url()),
            settings.EMAIL_FROM,
            settings.EMAIL_ADMIN_USERS,
            fail_silently=True,
        )
    except Exception as e:
        logger.error('No se pudo enviar correo electrónico', exc_info=e)


def send_notification(request, obj, model_name, created):
    """
    Sends an email notification about the creation or update of an object, unless the user is a superuser.
    
    Args:
        request: The HTTP request containing the user performing the action.
        obj: The object that was created or updated.
        model_name: The name of the object's model.
        created: Boolean indicating if the object was created (True) or updated (False).
    """
    if request.user.is_superuser:
        return

    try:
        send_mail(
            '{purpose} {model} "{obj}" by {user}'.format(
                purpose='Created new' if created else 'Updated',
                model=model_name,
                obj=str(obj),
                user=str(request.user),
            ),
            'https://desparchado.co{}'.format(obj.get_absolute_url()),
            settings.EMAIL_FROM,
            settings.EMAIL_ADMIN_USERS,
            fail_silently=True,
        )
    except:
        logger.error('No se pudo enviar correo electrónico')


def sanitize_html(html: str):
    """
    Sanitizes an HTML string by removing or altering potentially unsafe content.
    
    Args:
        html: The HTML string to sanitize.
    
    Returns:
        The sanitized HTML string with typographic whitespace preserved.
    """
    return sanitizer.sanitize(html)
