from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit
from django import forms
from django.urls import reverse_lazy

from desparchado.utils import sanitize_html
from events.models import Organizer


class OrganizerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """
        Initialize the OrganizerForm: require an image and configure Crispy FormHelper and layout.
        
        Sets the image field as required, creates and configures a FormHelper (form id 'organizer_form', POST method) and assigns a layout that includes the name field (with suggestion support via the organizer_suggestions URL), description, website URL, image, image source URL, and a submit button labeled "GUARDAR".
        """
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
        Sanitizes the form's cleaned 'description' value to remove unsafe HTML.
        
        Replaces the 'description' entry in the form's cleaned_data with the result of sanitize_html (uses an empty string if no description was provided) and returns the cleaned_data.
        
        Returns:
            dict: The form's cleaned_data with a sanitized 'description' value.
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