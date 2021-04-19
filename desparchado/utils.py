import logging

from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_admin_notification(request, obj, form, change):
    try:
        send_mail(
            '{purpose} {model} "{obj}" by {user}'.format(
                purpose='Updated' if change else 'Created new',
                model=form.Meta.model._meta.model_name,
                obj=str(obj),
                user=str(request.user),
            ),
            'http://desparchado.co{}'.format(obj.get_absolute_url()),
            settings.EMAIL_FROM,
            settings.EMAIL_ADMIN_USERS,
            fail_silently=True,
        )
    except:
        logger.error('No se pudo enviar correo electrónico')


def send_notification(request, obj, model_name, created):
    """
    Send notification about creation or edition of an object.
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
            'http://desparchado.co{}'.format(obj.get_absolute_url()),
            settings.EMAIL_FROM,
            settings.EMAIL_ADMIN_USERS,
            fail_silently=True,
        )
    except:
        logger.error('No se pudo enviar correo electrónico')
