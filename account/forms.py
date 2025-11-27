"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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


class UpdateProfileForm(ModelForm):  # type: ignore[type-arg]
    username = forms.CharField(max_length=150, required=True, label='Имя пользователя')
    first_name = forms.CharField(max_length=150, required=False, label='Имя')
    last_name = forms.CharField(max_length=150, required=False, label='Фамилия')
    email = forms.EmailField(max_length=150, required=True, label='Электронная почта')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
