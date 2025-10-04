from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms

from desparchado.utils import sanitize_html
from events.models import Speaker


class SpeakerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """
        Initialize the SpeakerForm, require the `image` field, and configure the Crispy Forms helper and layout.
        
        Sets `image` to required, creates a FormHelper with form_id "speaker_form" and method "post", and defines a layout containing the fields `name`, `description`, `image`, `image_source_url` plus a submit button labeled "GUARDAR".
        """
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
        Sanitizes the form's cleaned data so the 'description' field contains only safe HTML.
        
        The sanitized 'description' value replaces the original in the cleaned data.
        
        Returns:
            dict: Mapping of field names to cleaned values with 'description' sanitized.
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