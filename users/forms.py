from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div


User = get_user_model()


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
                Submit('submit', 'INGRESAR', css_class='btn-primary'),
                css_class='form-group',
            ),
        )


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=24)
    email = forms.EmailField(label='Correo electrónico')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'register_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'username',
            'first_name',
            'email',
            'password1',
            'password2',
            Div(
                Submit('submit', 'REGISTRARME', css_class='btn-primary'),
                css_class='form-group',
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email and User.objects.filter(email=email).first():
            self.add_error(
                'email',
                'Ya existe un usuario con este correo electrónico.',
            )
