from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, HTML, Field


class FilboEventCreateForm(forms.Form):
    spreadsheet_id = forms.CharField()
    worksheet_number = forms.IntegerField(initial=0)
    worksheet_range = forms.CharField(initial='A2:L10')

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with a custom layout and submission settings.
        
        Configures a helper to assign the form an ID of 'filbo_event_form' and to use the POST method.
        The layout is defined to include the 'spreadsheet_id', 'worksheet_number', and 'worksheet_range'
        fields, followed by a submit button labeled 'GUARDAR' styled with the 'btn-primary' class.
        Additional positional and keyword arguments are forwarded to the parent initializer.
        """
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'filbo_event_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'spreadsheet_id',
            'worksheet_number',
            'worksheet_range',
            Div(
                Submit('submit', 'GUARDAR', css_class='btn-primary'),
                css_class='form-group',
            ),
        )
