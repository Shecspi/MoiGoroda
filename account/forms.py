"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper  # type: ignore[import-untyped]
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from crispy_forms.layout import Layout, Field, Submit, Row, Column, HTML  # type: ignore[import-untyped]
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.safestring import mark_safe


class SignUpForm(UserCreationForm):  # type: ignore[type-arg]
    username = forms.CharField(label='Имя пользователя', required=True)
    email = forms.EmailField(label='Электронная почта', required=True)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(), required=True)
    password2 = forms.CharField(
        label='Повторите пароль', widget=forms.PasswordInput(), required=True
    )
    personal_data_consent = forms.BooleanField(
        label=mark_safe(
            'Я даю согласие на обработку моих персональных данных в соответствии с '
            '<a href="/privacy-policy" target="_blank">Политикой конфиденциальности</a>'
        ),
        required=False,
        widget=forms.CheckboxInput(attrs={'id': 'personal-data-consent'}),
    )
    personal_data_version = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Field('username'),
            Field('email'),
            Field('password1'),
            Field('password2'),
            Field('personal_data_consent'),
            Field('personal_data_version'),
        )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'personal_data_consent',
            'personal_data_version',
        )

    def clean_email(self) -> str:
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exists():
            raise ValidationError('Данный адрес электронной почты уже зарегистрирован.')

        return str(email) if email else ''


class SignInForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(Field('username'), Field('password'))


class UpdateProfileForm(ModelForm):  # type: ignore[type-arg]
    username = forms.CharField(max_length=150, required=True, label='Имя пользователя')
    first_name = forms.CharField(max_length=150, required=False, label='Имя')
    last_name = forms.CharField(max_length=150, required=False, label='Фамилия')
    email = forms.CharField(max_length=150, required=True, label='Электронная почта')

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('username'),
            Field('email'),
            Field('first_name'),
            Field('last_name'),
            Row(
                Column(
                    HTML("""<a href="{% url 'password_change_form' %}"
                    class="link-offset-2 link-underline-dark link-dark link-underline-opacity-50-hover 
                    link-opacity-50-hover">Изменить пароль</a>"""),
                    css_class='small',
                ),
                Column(
                    Submit('submit', 'Сохранить изменения', css_class='btn-success btn-block'),
                    css_class='d-flex justify-content-end',
                ),
                css_class='d-flex',
            ),
        )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
