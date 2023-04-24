from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse_lazy

from account.forms import SignUpForm


class SignUp_Test(TestCase):
    city_all_url = reverse_lazy('city-all')
    signup_url = reverse_lazy('signup')
    user = {'username': 'user', 'password': 'password'}

    def setUp(self) -> None:
        User.objects.create_user(
            username=self.user['username'],
            email='user@user.com',
            password=self.user['password']
        )

    def test_form_not_auth_user(self):
        """
        Неавторизованному пользователю форма регистрации показывается со статусом 200.
        """
        client = Client()
        response = client.get(self.signup_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')

        client.logout()

    def test_form_auth_user(self):
        """
        Авторизованный пользователь должен быть перенаправлен на /travel/city/all/.
        """
        client = Client()
        client.login(username=self.user['username'], password=self.user['password'])
        response = client.get(self.signup_url, follow=True)

        self.assertRedirects(response, self.city_all_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'travel/visited_city/news__list.html')

        client.logout()

    def test_form_has_fields(self):
        """
        Проверка наличия всех элементов формы.
        """
        form = SignUpForm()
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields, 'f')
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)

    def test_form_is_correct(self):
        """
        Проверка формы при вводе корректных данных.
        """
        data_correct = [
            # Полные данные
            {'username': 'test', 'email': 'test@test.com', 'first_name': 'first name',
             'last_name': 'last name', 'password1': 'psw', 'password2': 'psw'},
            # Тоже полные данные
            {'username': 'TEST', 'email': 'EMAIL@EMAIL.COM', 'first_name': 'FIRST NAME',
             'last_name': 'LAST NAME', 'password1': 'PSW', 'password2': 'PSW'},
            # First_name можно не указывать
            {'username': 'test', 'email': 'test@test.com',
             'last_name': 'last name', 'password1': 'psw', 'password2': 'psw'},
            # Last_name можно не указывать
            {'username': 'test', 'email': 'test@test.com', 'first_name': 'first name',
             'password1': 'psw', 'password2': 'psw'},
        ]

        for item in data_correct:
            form = SignUpForm(data=item)
            self.assertTrue(form.is_valid())

    def test_form_is_not_correct(self):
        """
        Проверка формы при вводе некорректных данных.
        """
        data_incorrect = [
            # Некорректный email
            {'username': 'test', 'email': 'emailemail.com', 'first_name': 'first name',
             'last_name': 'last name', 'password1': 'psw', 'password2': 'psw'},
            # Разные пароли
            {'username': 'TEST', 'email': 'EMAIL@EMAIL.COM', 'first_name': 'FIRST NAME',
             'last_name': 'LAST NAME', 'password1': 'PSW_', 'password2': 'PSW'},
            # Пользователь уже существует
            {'username': 'user', 'email': 'email@email.com', 'first_name': 'first name',
             'last_name': 'last name', 'password1': 'psw', 'password2': 'psw'},
            # Email уже существует
            {'username': 'test', 'email': 'user@user.com', 'first_name': 'first name',
             'last_name': 'last name', 'password1': 'psw', 'password2': 'psw'},
            # Не указан Username
            {'email': 'user@user.com', 'first_name': 'first name',
             'last_name': 'last name', 'password1': 'psw', 'password2': 'psw'},
            # Не указан Email
            {'username': 'test', 'first_name': 'first name',
             'last_name': 'last name', 'password1': 'psw', 'password2': 'psw'},
            # Не указан password1
            {'username': 'test', 'email': 'user@user.com', 'first_name': 'first name',
             'last_name': 'last name', 'password2': 'psw'},
            # Не указан password2
            {'username': 'test', 'email': 'user@user.com', 'first_name': 'first name',
             'last_name': 'last name', 'password1': 'psw'},
        ]

        for item in data_incorrect:
            form = SignUpForm(data=item)
            self.assertFalse(form.is_valid())
