import logging
from io import StringIO
from html.parser import HTMLParser

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
            'https://desparchado.co{}'.format(obj.get_absolute_url()),
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
            'https://desparchado.co{}'.format(obj.get_absolute_url()),
            settings.EMAIL_FROM,
            settings.EMAIL_ADMIN_USERS,
            fail_silently=True,
        )
    except:
        logger.error('No se pudo enviar correo electrónico')


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_html_tags(html: str):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
