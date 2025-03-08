from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout
from crispy_forms.layout import Div
from mapwidgets import GoogleMapPointFieldWidget
from desparchado.utils import strip_html_tags

from .models import Place


class PlaceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'place_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'name',
            'image',
            'image_source_url',
            'description',
            'website_url',
            'city',
            'location',
            Div(
                Submit('submit', 'GUARDAR', css_class='btn-primary'),
                css_class='form-group',
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['description'] = strip_html_tags(cleaned_data.get('description', ''))
        return cleaned_data

    class Meta:
        model = Place
        fields = (
            'name',
            'image',
            'image_source_url',
            'description',
            'website_url',
            'city',
            'location',
        )
        widgets = {
            'location': GoogleMapPointFieldWidget,
        }
