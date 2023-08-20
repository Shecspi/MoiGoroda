from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.safestring import mark_safe


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label='Имя пользователя',
        required=True)
    email = forms.EmailField(
        label='Электронная почта',
        required=True)
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(),
        required=True)
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(),
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Field('username'),
            Field('email'),
            Field('password1'),
            Field('password2')
        )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

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
            Field('username'),
            Field('password')
        )


class UpdateProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
