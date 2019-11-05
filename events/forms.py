from django import forms
from django.urls import reverse_lazy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout
from crispy_forms.layout import Div
from crispy_forms.layout import HTML
from crispy_forms.layout import Field
from crispy_forms.bootstrap import PrependedText
from crispy_forms.bootstrap import AppendedText
from dal import autocomplete

from .models import Event
from .models import Organizer
from .models import Speaker


class EventBaseForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get('event_date')
        event_end_date = cleaned_data.get('event_end_date')

        if event_date and event_end_date and event_date >= event_end_date:
            msg = 'Especifica una fecha de finalización igual ' \
                  'o posterior a la fecha de inicio.'
            self.add_error('event_end_date', msg)


class EventCreateForm(EventBaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['event_source_url'].required = True

        self.helper = FormHelper()
        self.helper.form_id = 'event_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'title',
            'description',
            'event_source_url',
            'image',
            Div(
                Div(
                    AppendedText(
                        'event_date',
                        '<i data-target="#id_event_date" '
                        '   data-toggle="datetimepicker" '
                        '   class="fa fa-calendar"></i>'
                    ),
                    data_target="#id_event_date",
                    css_class='input-group date col-md-6',
                ),
                Div(
                    AppendedText(
                        'event_end_date',
                        '<i data-target="#id_event_end_date" '
                        '   data-toggle="datetimepicker" '
                        '   class="fa fa-calendar"></i>'
                    ),
                    data_target="#event_end_date",
                    css_class='input-group date col-md-6',
                ),
                css_class='form-row',
            ),
            Div(
                Div('organizers', css_class='col-10'),
                Div(
                    HTML(
                        '<a href="{}" class="btn btn-light add-related" '
                        'title="Añadir nuevo organizador" target="_blank">'
                        '<i class="fas fa-plus"></i>'
                        '</a>'.format(
                            reverse_lazy('events:organizer_add'),
                        )
                    ),
                    css_class='col-2'
                ),
                css_class='form-row',
            ),
            Div(
                Div('place', css_class='col-10'),
                Div(
                    HTML(
                        '<a href="{}" class="btn btn-light add-related" '
                        'title="Añadir nuevo presentador" target="_blank">'
                        '<i class="fas fa-plus"></i>'
                        '</a>'.format(
                            reverse_lazy('places:place_add'),
                        )
                    ),
                    css_class='col-2'
                ),
                css_class='form-row',
            ),
            Div(
                Submit('submit', 'PUBLICAR EVENTO', css_class='btn-primary'),
                css_class='form-group',
            ),
        )

    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'event_source_url',
            'image',
            'event_date',
            'event_end_date',
            'organizers',
            'place',
        ]
        widgets = {
            'organizers':
            autocomplete.ModelSelect2Multiple(
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


class EventUpdateForm(EventBaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['event_source_url'].required = True

        self.helper = FormHelper()
        self.helper.form_id = 'event_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'title',
            'is_published',
            'description',
            'event_source_url',
            'image',
            'image_source_url',
            Div(
                Div('event_type', css_class='col-md-6'),
                Div('topic', css_class='col-md-6'),
                css_class='form-row',
            ),
            Div(
                Div(
                    AppendedText(
                        'event_date',
                        '<i data-target="#id_event_date" '
                        '   data-toggle="datetimepicker" '
                        '   class="fa fa-calendar"></i>'
                    ),
                    data_target="#id_event_date",
                    css_class='input-group date col-md-6',
                ),
                Div(
                    AppendedText(
                        'event_end_date',
                        '<i data-target="#id_event_end_date" '
                        '   data-toggle="datetimepicker" '
                        '   class="fa fa-calendar"></i>'
                    ),
                    data_target="#event_end_date",
                    css_class='input-group date col-md-6',
                ),
                css_class='form-row',
            ),
            PrependedText('price', '$'),
            Div(
                Div('organizers', css_class='col-10'),
                Div(
                    HTML(
                        '<a href="{}" class="btn btn-light add-related" '
                        'title="Añadir nuevo organizador" target="_blank">'
                        '<i class="fas fa-plus"></i>'
                        '</a>'.format(
                            reverse_lazy('events:organizer_add'),
                        )
                    ),
                    css_class='col-2'
                ),
                css_class='form-row',
            ),
            Div(
                Div('place', css_class='col-10'),
                Div(
                    HTML(
                        '<a href="{}" class="btn btn-light add-related" '
                        'title="Añadir nuevo presentador" target="_blank">'
                        '<i class="fas fa-plus"></i>'
                        '</a>'.format(
                            reverse_lazy('places:place_add'),
                        )
                    ),
                    css_class='col-2'
                ),
                css_class='form-row',
            ),
            Div(
                Div('speakers', css_class='col-10'),
                Div(
                    HTML(
                        '<a href="{}" class="btn btn-light add-related" '
                        'title="Añadir nuevo presentador" target="_blank">'
                        '<i class="fas fa-plus"></i>'
                        '</a>'.format(
                            reverse_lazy('events:speaker_add'),
                        )
                    ),
                    css_class='col-2'
                ),
                css_class='form-row',
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
            'organizers',
            'place',
            'speakers',
        ]
        widgets = {
            'organizers':
            autocomplete.ModelSelect2Multiple(
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
