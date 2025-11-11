from crispy_bootstrap5.bootstrap5 import Switch
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Layout, Submit
from dal import autocomplete
from django import forms
from django.urls import reverse_lazy

from desparchado.utils import sanitize_html
from events.models import Event


class EventBaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['event_source_url'].required = True

        self.helper = FormHelper()
        self.helper.form_id = 'event_form'
        self.helper.form_method = 'post'

    def clean(self):
        """
        Sanitizes the event description and returns cleaned data.
        """
        cleaned_data = super().clean()

        cleaned_data['description'] = sanitize_html(cleaned_data.get('description', ''))

        return cleaned_data

    @staticmethod
    def get_organizer_button():
        return Div(
            HTML(
                f'<a href="{reverse_lazy("events:organizer_add")}" '
                'class="btn btn-light" '
                'title="Añadir nuevo organizador" target="_blank">'
                '<i class="fas fa-plus"></i> Añadir nuevo organizador'
                '</a>',
            ),
            css_class='mb-3',
        )

    @staticmethod
    def get_place_button():
        return Div(
            HTML(
                f'<a href="{reverse_lazy("places:place_add")}" class="btn btn-light" '
                'title="Añadir nuevo lugar" target="_blank">'
                '<i class="fas fa-plus"></i> Añadir nuevo lugar'
                '</a>',
            ),
            css_class='mb-3',
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
            'category',
            'event_date',
            'price',
            'organizers',
            'place',
            'speakers',
        ]
        widgets = {
            'organizers': autocomplete.ModelSelect2Multiple(
                url='events:organizer_autocomplete',
                attrs={
                    'data-html': True,
                    'data-theme': 'bootstrap-5',
                },
            ),
            'place': autocomplete.ModelSelect2(
                url='places:place_autocomplete',
                attrs={
                    'data-html': True,
                    'data-theme': 'bootstrap-5',
                },
            ),
            'speakers': autocomplete.ModelSelect2Multiple(
                url='events:speaker_autocomplete',
                attrs={
                    'data-html': True,
                    'data-theme': 'bootstrap-5',
                },
            ),
        }


class EventCreateForm(EventBaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            'title',
            'description',
            'event_source_url',
            'image',
            'category',
            'event_date',
            'organizers',
            self.get_organizer_button(),
            'place',
            self.get_place_button(),
            Div(
                Submit('submit', 'PUBLICAR EVENTO', css_class='btn-primary'),
                css_class='form-group mt-3',
            ),
        )

    class Meta(EventBaseForm.Meta):
        fields = [
            "title",
            "description",
            "event_source_url",
            "image",
            "category",
            "event_date",
            "organizers",
            "place",
        ]


class EventUpdateForm(EventBaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            'title',
            Switch('is_published'),
            'description',
            'event_source_url',
            'image',
            'image_source_url',
            'category',
            'event_date',
            PrependedText('price', '$'),
            'organizers',
            self.get_organizer_button(),
            'place',
            self.get_place_button(),
            'speakers',
            Div(
                HTML(
                    f'<a href="{reverse_lazy("events:speaker_add")}" '
                    'class="btn btn-light" '
                    'title="Añadir nuevo presentador" target="_blank">'
                    '<i class="fas fa-plus"></i> Añadir nuevo presentador'
                    '</a>',
                ),
            ),
            Div(
                Submit('submit', 'GUARDAR', css_class='btn-primary'),
                css_class='form-group mt-3',
            ),
        )
