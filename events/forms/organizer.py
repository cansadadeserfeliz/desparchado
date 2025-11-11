from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit
from django import forms
from django.urls import reverse_lazy

from desparchado.utils import sanitize_html
from events.models import Organizer


class OrganizerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["image"].required = True

        self.helper = FormHelper()
        self.helper.form_id = 'organizer_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Field(
                'name',
                css_class='show-suggestions',
                data_suggestions_url=reverse_lazy('events:organizer_suggestions'),
            ),
            'description',
            'website_url',
            'image',
            'image_source_url',
            Div(
                Submit('submit', 'GUARDAR', css_class='btn-primary'),
                css_class='form-group',
            ),
        )

    def clean(self):
        """
        Cleans and sanitizes the description field to remove unsafe HTML content.

        Returns:
            The cleaned form data with a sanitized description.
        """
        cleaned_data = super().clean()
        cleaned_data['description'] = sanitize_html(cleaned_data.get('description', ''))
        return cleaned_data

    class Meta:
        model = Organizer
        fields = [
            'name',
            'description',
            'website_url',
            'image',
            'image_source_url',
        ]
