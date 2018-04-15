from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout
from crispy_forms.layout import Div
from crispy_forms.layout import Fieldset
from crispy_forms.bootstrap import PrependedText
from dal import autocomplete

from .models import Event


class EventCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['event_source_url'].required = True

        self.helper = FormHelper()
        self.helper.form_id = 'event_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'title',
            'is_published',
            Fieldset(
                'Información básica',
                'description',
                'event_source_url',
                'image',
                'image_source_url',
                Div(
                    Div('event_type', css_class='col-md-6'),
                    Div('topic', css_class='col-md-6'),
                    css_class='row',
                ),
            ),
            Fieldset(
                'Fechas',
                Div(
                    Div('event_date', css_class='col-md-6'),
                    Div('event_end_date', css_class='col-md-6'),
                    css_class='row',
                ),
            ),
            PrependedText('price', '$'),
            'organizer',
            'place',
            'speakers',
            Div(
                Submit('submit', 'GUARDAR EVENTO', css_class='btn-primary'),
                css_class='form-group',
            ),
        )

    class Meta:
        model = Event
        fields = [
            'title',
            'is_published',
            'description',
            'event_source_url',
            'image',
            'image_source_url',
            'event_type',
            'topic',
            'event_date',
            'event_end_date',
            'price',
            'organizer',
            'place',
            'speakers',
        ]
        widgets = {
            'organizer':
            autocomplete.ModelSelect2(
                url='events:organizer_autocomplete',
                attrs={
                    'data-html': True,
                },
            ),
            'place':
            autocomplete.ModelSelect2(
                url='places:place_autocomplete',
                attrs={
                    'data-html': True,
                },
            ),
            'speakers':
            autocomplete.ModelSelect2Multiple(
                url='events:speaker_autocomplete',
                attrs={
                    'data-html': True,
                },
            )
        }


