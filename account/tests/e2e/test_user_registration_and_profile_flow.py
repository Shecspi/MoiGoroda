"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from account.models import UserConsent


# ===== E2E тесты для регистрации и профиля =====


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.access.logger_email')
def test_complete_user_registration_and_profile_update_flow(mock_logger, client):
    """
    E2E тест: Регистрация пользователя -> Вход -> Обновление профиля -> Выход
    """
    # Шаг 1: Открываем страницу регистрации
    response = client.get(reverse('signup'))
    assert response.status_code == 200
    assert 'Регистрация' in response.context['page_title']

    # Шаг 2: Регистрируем пользователя
    signup_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'TestPass123!',
        'password2': 'TestPass123!',
        'personal_data_consent': True,
        'personal_data_version': '1.0',
    }
    response = client.post(reverse('signup'), data=signup_data, follow=True)

    # Проверяем, что пользователь создан и авторизован
    assert response.status_code == 200
    assert User.objects.filter(username='newuser').exists()
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.username == 'newuser'

    # Проверяем, что UserConsent создан
    user = User.objects.get(username='newuser')
    assert UserConsent.objects.filter(user=user).exists()

    # Шаг 3: Выходим из системы
    response = client.post(reverse('logout'), follow=True)
    assert not response.wsgi_request.user.is_authenticated

    # Шаг 4: Входим снова
    response = client.post(
        reverse('signin'), data={'username': 'newuser', 'password': 'TestPass123!'}, follow=True
    )
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.username == 'newuser'

    # Шаг 5: Переходим на страницу профиля
    response = client.get(reverse('profile'))
    assert response.status_code == 200
    assert 'Профиль' in response.context['page_title']

    # Шаг 6: Обновляем профиль
    with patch('account.views.profile.logger'):
        update_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
        }
        response = client.post(reverse('profile'), data=update_data, follow=True)

    assert response.status_code == 200

    # Проверяем, что данные обновились
    user.refresh_from_db()
    assert user.username == 'updateduser'
    assert user.email == 'updated@example.com'
    assert user.first_name == 'John'
    assert user.last_name == 'Doe'

    # Шаг 7: Проверяем, что можем зайти с обновлённым username
    client.post(reverse('logout'))
    response = client.post(
        reverse('signin'),
        data={'username': 'updateduser', 'password': 'TestPass123!'},
        follow=True,
    )
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.username == 'updateduser'


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.access.logger_email')
def test_registration_with_invalid_data_then_correction(mock_logger, client):
    """
    E2E тест: Попытка регистрации с невалидными данными -> Исправление -> Успешная регистрация
    """
    # Шаг 1: Попытка регистрации с невалидным email
    invalid_data = {
        'username': 'testuser',
        'email': 'invalid-email',
        'password1': 'TestPass123!',
        'password2': 'TestPass123!',
        'personal_data_consent': True,
        'personal_data_version': '1.0',
    }
    response = client.post(reverse('signup'), data=invalid_data)

    assert response.status_code == 200
    assert not User.objects.filter(username='testuser').exists()
    assert 'email' in response.context['form'].errors

    # Шаг 2: Исправляем данные и регистрируемся успешно
    valid_data = invalid_data.copy()
    valid_data['email'] = 'valid@example.com'
    response = client.post(reverse('signup'), data=valid_data, follow=True)

    assert response.status_code == 200
    assert User.objects.filter(username='testuser').exists()
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.e2e
@pytest.mark.django_db
def test_change_password_flow(client, django_user_model):
    """
    E2E тест: Вход -> Изменение пароля -> Выход -> Вход с новым паролем
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='OldPass123!')

    # Шаг 2: Входим в систему
    client.force_login(user)

    # Шаг 3: Открываем страницу изменения пароля
    response = client.get(reverse('password_change_form'))
    assert response.status_code == 200

    # Шаг 4: Изменяем пароль
    response = client.post(
        reverse('password_change_form'),
        data={
            'old_password': 'OldPass123!',
            'new_password1': 'NewPass123!',
            'new_password2': 'NewPass123!',
        },
        follow=True,
    )
    assert response.status_code == 200

    # Шаг 5: Выходим из системы
    client.post(reverse('logout'))

    # Шаг 6: Пытаемся войти со старым паролем - должно не получиться
    response = client.post(
        reverse('signin'), data={'username': 'testuser', 'password': 'OldPass123!'}
    )
    assert not response.wsgi_request.user.is_authenticated

    # Шаг 7: Входим с новым паролем
    response = client.post(
        reverse('signin'), data={'username': 'testuser', 'password': 'NewPass123!'}, follow=True
    )
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.username == 'testuser'


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.access.logger_email')
def test_registration_duplicate_email_handling(mock_logger, client, django_user_model):
    """
    E2E тест: Регистрация пользователя -> Попытка регистрации с тем же email
    """
    # Шаг 1: Регистрируем первого пользователя
    first_user_data = {
        'username': 'firstuser',
        'email': 'same@example.com',
        'password1': 'TestPass123!',
        'password2': 'TestPass123!',
        'personal_data_consent': True,
        'personal_data_version': '1.0',
    }
    response = client.post(reverse('signup'), data=first_user_data, follow=True)
    assert User.objects.filter(username='firstuser').exists()

    # Выходим
    client.post(reverse('logout'))

    # Шаг 2: Пытаемся зарегистрировать второго пользователя с тем же email
    second_user_data = {
        'username': 'seconduser',
        'email': 'same@example.com',  # Тот же email
        'password1': 'TestPass123!',
        'password2': 'TestPass123!',
        'personal_data_consent': True,
        'personal_data_version': '1.0',
    }
    response = client.post(reverse('signup'), data=second_user_data)

    # Проверяем, что регистрация не прошла
    assert response.status_code == 200
    assert not User.objects.filter(username='seconduser').exists()
    assert 'email' in response.context['form'].errors

    # Шаг 3: Исправляем email и регистрируемся успешно
    second_user_data['email'] = 'different@example.com'
    response = client.post(reverse('signup'), data=second_user_data, follow=True)
    assert User.objects.filter(username='seconduser').exists()


@pytest.mark.e2e
@pytest.mark.django_db
def test_profile_update_preserves_authentication(client, django_user_model):
    """
    E2E тест: Обновление профиля не разлогинивает пользователя
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(
        username='testuser', email='test@example.com', password='password123'
    )
    client.force_login(user)

    # Шаг 2: Обновляем профиль
    with patch('account.views.profile.logger'):
        update_data = {
            'username': 'newusername',
            'email': 'newemail@example.com',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = client.post(reverse('profile'), data=update_data, follow=True)

    # Проверяем, что пользователь всё ещё авторизован
    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.username == 'newusername'

    # Шаг 3: Проверяем, что можем обратиться к профилю снова
    response = client.get(reverse('profile'))
    assert response.status_code == 200
    form = response.context['form']
    assert form.initial['username'] == 'newusername'
    assert form.initial['email'] == 'newemail@example.com'


@pytest.mark.e2e
@pytest.mark.django_db
def test_authenticated_user_cannot_access_signup_or_signin(client, django_user_model):
    """
    E2E тест: Авторизованный пользователь не может попасть на страницы регистрации/входа
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Пытаемся зайти на страницу регистрации
    response = client.get(reverse('signup'))
    assert response.status_code == 302
    assert response.url == reverse('city-all-list')

    # Шаг 3: Пытаемся зайти на страницу входа
    response = client.get(reverse('signin'))
    assert response.status_code == 302
    assert response.url == reverse('city-all-list')


@pytest.mark.e2e
@pytest.mark.django_db
def test_unauthenticated_user_redirected_to_signin_from_profile(client):
    """
    E2E тест: Неавторизованный пользователь перенаправляется на вход при попытке доступа к профилю
    """
    # Шаг 1: Пытаемся зайти на страницу профиля без авторизации
    response = client.get(reverse('profile'))

    assert response.status_code == 302
    assert response.url.startswith('/account/signin')

    # Шаг 2: Переходим по редиректу
    response = client.get(reverse('profile'), follow=True)

    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.access.logger_email')
def test_full_user_journey_with_password_change(mock_logger, client):
    """
    E2E тест: Полный путь пользователя - регистрация -> профиль -> изменение пароля -> выход -> вход
    """
    # Шаг 1: Регистрация
    signup_data = {
        'username': 'journeyuser',
        'email': 'journey@example.com',
        'password1': 'InitialPass123!',
        'password2': 'InitialPass123!',
        'personal_data_consent': True,
        'personal_data_version': '1.0',
    }
    response = client.post(reverse('signup'), data=signup_data, follow=True)
    assert response.wsgi_request.user.is_authenticated

    # Шаг 2: Обновление профиля
    with patch('account.views.profile.logger'):
        response = client.post(
            reverse('profile'),
            data={
                'username': 'journeyuser',
                'email': 'journey@example.com',
                'first_name': 'Journey',
                'last_name': 'Tester',
            },
            follow=True,
        )
    assert response.status_code == 200

    user = User.objects.get(username='journeyuser')
    assert user.first_name == 'Journey'
    assert user.last_name == 'Tester'

    # Шаг 3: Изменение пароля
    response = client.post(
        reverse('password_change_form'),
        data={
            'old_password': 'InitialPass123!',
            'new_password1': 'UpdatedPass123!',
            'new_password2': 'UpdatedPass123!',
        },
        follow=True,
    )
    assert response.status_code == 200

    # Шаг 4: Выход
    client.post(reverse('logout'))

    # Шаг 5: Вход с новым паролем
    response = client.post(
        reverse('signin'),
        data={'username': 'journeyuser', 'password': 'UpdatedPass123!'},
        follow=True,
    )
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.username == 'journeyuser'

    # Шаг 6: Проверяем профиль
    response = client.get(reverse('profile'))
    assert response.status_code == 200
    form = response.context['form']
    assert form.initial['first_name'] == 'Journey'
    assert form.initial['last_name'] == 'Tester'
