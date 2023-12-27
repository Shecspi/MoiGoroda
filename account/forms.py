from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from crispy_forms.layout import Layout, Field, Submit, Row, Column, HTML
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


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
    username = forms.CharField(max_length=150, required=True, label='Имя пользователя')
    first_name = forms.CharField(max_length=150, required=False, label='Имя')
    last_name = forms.CharField(max_length=150, required=False, label='Фамилия')
    email = forms.CharField(max_length=150, required=True, label='Электронная почта')

    def __init__(self, *args, **kwargs):
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
                    css_class='small'
                ),
                Column(
                    Submit('submit', 'Сохранить изменения', css_class='btn-success btn-block'),
                    css_class='d-flex justify-content-end'
                ),
                css_class='d-flex'
            )
        )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
