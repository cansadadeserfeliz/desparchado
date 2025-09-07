from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.utils.translation import gettext_lazy as _


class SpreadsheetSyncForm(forms.Form):
    spreadsheet_id = forms.CharField()
    worksheet_number = forms.IntegerField(initial=0)
    worksheet_range = forms.CharField(initial='A2:L100')
    event_id_field = forms.ChoiceField(
        choices=[('event_source_url', 'event_source_url')],
        initial='event_source_url',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'spreadsheet_sync_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'spreadsheet_id',
            'worksheet_number',
            'worksheet_range',
            'event_id_field',
            Div(
                Submit('submit', _('Sincronizar'), css_class='btn-primary'),
                css_class='form-group',
            ),
        )
