from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout
from crispy_forms.layout import Div

from .models import HuntingOfSnarkGame


class HuntingOfSnarkGameCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'game_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'player_name',
            'total_points',
            Div(
                Submit('submit', 'Generar juego', css_class='btn-primary'),
                css_class='form-group',
            ),
        )

    class Meta:
        model = HuntingOfSnarkGame
        fields = [
            'player_name',
            'total_points',
        ]
