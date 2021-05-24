from django.db import models
from django.conf import settings


class EditorsModel(models.Model):
    """
    An abstract base class model that provides
    ``created_by`` and ``editors`` fields
    and ``can_edit`` method.

    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        verbose_name='Creado por',
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
    )

    def can_edit(self, user):
        if user.is_superuser or user == self.created_by or user in self.editors.all():
            return True
        return False

    class Meta:
        abstract = True
