from dal import autocomplete
from django.utils.html import format_html


class BaseAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, result):
        return format_html(
            '<img src="{}" height="20"> {}', result.get_image_url(), result.name,
        )

    def get_selected_result_label(self, result):
        return result.name
