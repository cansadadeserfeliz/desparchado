from django import forms
from django.urls import reverse_lazy
from django.core.validators import MinValueValidator
from django.utils import timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout
from crispy_forms.layout import Div
from crispy_forms.layout import HTML


class PostsSearchForm(forms.Form):
    start_date = forms.IntegerField(
        label='Fecha inicio',
        validators=[
            MinValueValidator(1400, message='La fecha debe ser mayor a 1400'),
        ],
        required=False,
    )
    end_date = forms.IntegerField(
        label='Fecha final',
        validators=[
            MinValueValidator(1400, message='La fecha debe ser mayor a 1400'),
        ],
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        current_year = timezone.now().year
        current_year_error_message = f'El año debe ser menor o igual a {current_year}'
        if start_date and start_date > current_year:
            self.add_error('start_date', current_year_error_message)
        if end_date and end_date > current_year:
            self.add_error('end_date', current_year_error_message)

        if start_date and end_date:
            if end_date < start_date:
                self.add_error(
                    'start_date',
                    'La fecha de inicio debe ser menor a la fecha final.'
                )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'posts_search_form'
        self.helper.form_method = 'get'
        self.helper.form_class = 'row'

        self.helper.layout = Layout(
            Div(
                'start_date',
                css_class='col',
            ),
            Div(
                'end_date',
                css_class='col',
            ),
            Div(
                Submit('submit', 'Filtrar', css_class='btn-primary'),
                HTML(
                    '<a href="{}" class="btn btn-primary">Limpiar</a>'.format(
                        reverse_lazy('history:index'),
                    )
                ),
                css_class='col',
            ),
        )
