from django import forms
from django.urls import reverse_lazy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout
from crispy_forms.layout import Div
from crispy_forms.layout import HTML
from crispy_forms.layout import Fieldset
from crispy_forms.layout import Field
from crispy_forms.bootstrap import PrependedText
from dal import autocomplete

from .models import Event
from .models import Organizer
from .models import Speaker


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
            Div(
                Div('organizer', css_class='col-xs-10'),
                Div(
                    HTML(
                        '<a href="{}" class="btn btn-default add-related" '
                        'title="Añadir nuevo organizador" target="_blank">'
                        '<i class="fa fa-plus"></i>'
                        '</a>'.format(
                            reverse_lazy('events:organizer_add'),
                        )
                    ),
                    css_class='col-xs-2'
                ),
                css_class='row',
            ),
            Div(
                Div('place', css_class='col-xs-10'),
                Div(
                    HTML(
                        '<a href="{}" class="btn btn-default add-related" '
                        'title="Añadir nuevo presentador" target="_blank">'
                        '<i class="fa fa-plus"></i>'
                        '</a>'.format(
                            reverse_lazy('places:place_add'),
                        )
                    ),
                    css_class='col-xs-2'
                ),
                css_class='row',
            ),
            Div(
                Div('speakers', css_class='col-xs-10'),
                Div(
                    HTML(
                        '<a href="{}" class="btn btn-default add-related" '
                        'title="Añadir nuevo presentador" target="_blank">'
                        '<i class="fa fa-plus"></i>'
                        '</a>'.format(
                            reverse_lazy('events:speaker_add'),
                        )
                    ),
                    css_class='col-xs-2'
                ),
                css_class='row',
            ),
            Div(
                Submit('submit', 'GUARDAR', css_class='btn-primary'),
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

    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get('event_date')
        event_end_date = cleaned_data.get('event_end_date')

        if event_date and event_end_date and event_date >= event_end_date:
            msg = 'Especifique una fecha de finalización igual ' \
                  'o posterior a la fecha de inicio.'
            self.add_error('event_end_date', msg)


class OrganizerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'organizer_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Field(
                'name',
                css_class='show-suggestions',
                data_suggestions_url=
                reverse_lazy('events:organizer_suggestions'),
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

    class Meta:
        model = Organizer
        fields = [
            'name',
            'description',
            'website_url',
            'image',
            'image_source_url',
        ]


class SpeakerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    class Meta:
        model = Speaker
        fields = [
            'name',
            'description',
            'image',
            'image_source_url',
        ]
