from django.contrib.auth.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'login_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'username',
            'password',
            Div(
                Submit('submit', 'Ingresar', css_class='btn-default'),
                css_class='form-group',
            ),
        )
