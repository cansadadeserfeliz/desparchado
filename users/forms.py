from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm as AuthPasswordResetForm
from django.contrib.auth.forms import SetPasswordForm as AuthSetPasswordForm
from django.contrib.auth import get_user_model
from django import forms
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

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


class PasswordResetForm(AuthPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'password_reset_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'email',
            Div(
                Submit('submit', 'RESTABLECER CONTRASEÑA', css_class='btn-primary'),
                css_class='form-group',
            ),
        )

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, settings.EMAIL_FROM, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()


class SetPasswordForm(AuthSetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'password_reset_form'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'new_password1',
            'new_password2',
            Div(
                Submit('submit', 'CAMBIAR MI CONTRASEÑA', css_class='btn-primary'),
                css_class='form-group',
            ),
        )
