from django.db import models
from django.utils.translation import gettext_lazy as _


class SpreadsheetSync(models.Model):
    """Defines configuration for spreadsheet events syncs."""

    title = models.CharField(
        verbose_name=_("Título"),
        max_length=255,
    )
    spreadsheet_id = models.CharField(
        verbose_name=_("Google Sheets spreadsheet key"),
        max_length=255,
    )
    worksheet_number = models.IntegerField(
        verbose_name=_("Worksheet number"),
        default=0,
    )

    class EventIdField(models.TextChoices):
        EVENT_SOURCE_URL = "event_source_url", _("Event URL")
        SOURCE_ID = "source_id", _("Source ID")

    event_id_field = models.CharField(
        verbose_name=_("Event model field used to identify records"),
        choices=EventIdField,
        help_text=_(
            "Campo utilizado para encontrar eventos existentes "
            "durante la sincronización",
        ),
    )
    special = models.ForeignKey(
        "specials.Special",
        verbose_name=_("Special that will be assigned to the events"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    is_hidden = models.BooleanField(
        verbose_name=_("If the event will be hidden on home"),
        default=False,
    )

    class Meta:
        verbose_name = _("Spreadsheet Sync")
        verbose_name_plural = _("Spreadsheet Syncs")
        unique_together = ('spreadsheet_id', 'worksheet_number')

    def __str__(self):
        return f"{self.title} ({self.spreadsheet_id} - {self.worksheet_number})"
