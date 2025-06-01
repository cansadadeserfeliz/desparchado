from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit
from django import forms


class FilboEventCreateForm(forms.Form):
    spreadsheet_id = forms.CharField()
    worksheet_number = forms.IntegerField(initial=0)
    worksheet_range = forms.CharField(initial='A2:L10')

    def __init__(self, *args, **kwargs):
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
