from django.contrib import admin

from .models import SpreadsheetSync


@admin.register(SpreadsheetSync)
class SpreadsheetSyncAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "spreadsheet_id",
        "worksheet_number",
        "event_id_field",
        "special",
        "is_hidden",
    )
    list_select_related = ("special",)
