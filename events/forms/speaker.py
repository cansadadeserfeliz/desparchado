from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms

from desparchado.utils import sanitize_html
from events.models import Speaker


class SpeakerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["image"].required = True

        self.helper = FormHelper()
        self.helper.form_id = 'speaker_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'name',
            'description',
            'image',
            'image_source_url',
            Div(
                Submit('submit', 'GUARDAR', css_class='btn-primary'),
                css_class='form-group',
            ),
        )

    def clean(self):
        """
        Cleans and sanitizes the form data, ensuring the description field contains
        only safe HTML.

        Returns:
            The cleaned and sanitized form data.
        """
        cleaned_data = super().clean()
        cleaned_data['description'] = sanitize_html(cleaned_data.get('description', ''))
        return cleaned_data

    class Meta:
        model = Speaker
        fields = [
            'name',
            'description',
            'image',
            'image_source_url',
        ]
