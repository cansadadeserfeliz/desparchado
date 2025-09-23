from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from dashboard.models import SpreadsheetSync


class SpreadsheetSyncForm(forms.Form):
    spreadsheet_sync = forms.ModelChoiceField(
        queryset=SpreadsheetSync.objects.all(),
        required=True,
    )
    worksheet_range = forms.CharField(initial='A2:L100')

    def __init__(self, *args, **kwargs):
        """Initialize the form and configure a Crispy-Forms FormHelper for rendering.
        """
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'spreadsheet_sync_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'spreadsheet_sync',
            'worksheet_range',
            Div(
                Submit('submit', _('Sincronizar'), css_class='btn-primary'),
                css_class='form-group',
            ),
        )
