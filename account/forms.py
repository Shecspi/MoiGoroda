from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label='Имя пользователя',
        help_text='Указанное имя пользователя будет использовано для авторизации на сайте.',
        required=True)
    email = forms.EmailField(
        label='Электронная почта',
        help_text='Проверьте правильность указанного email. '
                  'Этот адрес будет использован для восстановления пароля, если Вы его забудете.',
        required=True)
    first_name = forms.CharField(
        label='Имя',
        required=False)
    last_name = forms.CharField(
        label='Фамилия',
        required=False)
    password1 = forms.CharField(
        label='Пароль',
        help_text='Мы не вводим никаких ограничений по сложности пароля, но всегда помните, что пароль должен быть '
                  'достаточно длинным, а также содержать буквы, цифры и специальные символы. Это нужно для '
                  'безопасности Вашего аккаунта.',
        widget=forms.PasswordInput(),
        required=True)
    password2 = forms.CharField(
        label='Повторите пароль',
        help_text='Для того, чтобы избежать возможности появления ошибки, пожалуйста, повторите пароль ещё раз.',
        widget=forms.PasswordInput(),
        required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError('Данный адрес электронной почты уже зарегистрирован.')

        return email


class SignInForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            PrependedText('username', '<i class="bi bi-person"></i>'),
            PrependedText('password', '<i class="bi bi-lock"></i>')
        )


class UpdateProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
