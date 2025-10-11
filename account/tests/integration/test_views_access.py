"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from account.models import UserConsent


# ===== Фикстуры =====


@pytest.fixture
def user_data() -> dict[str, Any]:
    """Данные для создания пользователя"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'TestPass123!',
        'password2': 'TestPass123!',
        'personal_data_consent': True,
        'personal_data_version': '1.0',
    }


# ===== Тесты для SignUp =====


@pytest.mark.integration
@pytest.mark.django_db
def test_signup_view_get_request(client: Any) -> None:
    """Тест GET запроса на страницу регистрации"""
    response = client.get(reverse('signup'))

    assert response.status_code == 200
    assert 'account/signup.html' in (t.name for t in response.templates)
    assert 'Регистрация' in response.context['page_title']


@pytest.mark.integration
@pytest.mark.django_db
def test_signup_view_authenticated_user_redirect(client: Any, django_user_model: Any) -> None:
    """Тест что авторизованный пользователь перенаправляется со страницы регистрации"""
    user = django_user_model.objects.create_user(username='existinguser', password='password123')
    client.force_login(user)

    response = client.get(reverse('signup'))

    assert response.status_code == 302
    assert response.url == reverse('city-all-list')


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.access.logger_email')
def test_signup_view_post_valid_data(mock_logger: Any, client: Any, user_data: dict[str, Any]) -> None:
    """Тест успешной регистрации пользователя"""
    response = client.post(reverse('signup'), data=user_data, follow=True)

    # Проверяем, что пользователь создан
    assert User.objects.filter(username='testuser').exists()
    user = User.objects.get(username='testuser')
    assert user.email == 'test@example.com'

    # Проверяем, что UserConsent создан
    assert UserConsent.objects.filter(user=user).exists()
    consent = UserConsent.objects.get(user=user)
    assert consent.consent_given is True
    assert consent.policy_version is not None

    # Проверяем, что пользователь авторизован
    assert response.wsgi_request.user.is_authenticated

    # Проверяем редирект
    assert response.status_code == 200
    assert response.redirect_chain[-1][0] == reverse('city-all-list')

    # Проверяем, что логирование произошло
    mock_logger.info.assert_called_once()


@pytest.mark.integration
@pytest.mark.django_db
def test_signup_view_post_invalid_data(client: Any) -> None:
    """Тест регистрации с невалидными данными"""
    invalid_data = {
        'username': 'testuser',
        'email': 'invalid-email',
        'password1': '123',
        'password2': '456',
    }

    response = client.post(reverse('signup'), data=invalid_data)

    assert response.status_code == 200
    assert not User.objects.filter(username='testuser').exists()
    assert 'form' in response.context
    assert response.context['form'].errors


@pytest.mark.integration
@pytest.mark.django_db
def test_signup_view_duplicate_email(client: Any, user_data: dict[str, Any], django_user_model: Any) -> None:
    """Тест регистрации с уже существующим email"""
    # Создаём пользователя с таким же email
    django_user_model.objects.create_user(
        username='existinguser', email='test@example.com', password='password123'
    )

    response = client.post(reverse('signup'), data=user_data)

    assert response.status_code == 200
    assert not User.objects.filter(username='testuser').exists()
    assert 'email' in response.context['form'].errors


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.access.logger_email')
def test_signup_view_ip_address_saved(mock_logger: Any, client: Any, user_data: dict[str, Any]) -> None:
    """Тест что IP адрес сохраняется при регистрации"""
    # Устанавливаем IP адрес через заголовок
    client.post(reverse('signup'), data=user_data, HTTP_X_FORWARDED_FOR='192.168.1.1,10.0.0.1')

    user = User.objects.get(username='testuser')
    consent = UserConsent.objects.get(user=user)

    # Должен быть сохранён первый IP из списка
    assert consent.ip_address == '192.168.1.1'


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.access.logger_email')
def test_signup_view_ip_address_remote_addr(mock_logger: Any, client: Any, user_data: dict[str, Any]) -> None:
    """Тест что IP адрес сохраняется из REMOTE_ADDR если нет X-Forwarded-For"""
    client.post(reverse('signup'), data=user_data, REMOTE_ADDR='10.0.0.2')

    user = User.objects.get(username='testuser')
    consent = UserConsent.objects.get(user=user)

    assert consent.ip_address == '10.0.0.2'


# ===== Тесты для SignIn =====


@pytest.mark.integration
@pytest.mark.django_db
def test_signin_view_get_request(client: Any) -> None:
    """Тест GET запроса на страницу входа"""
    response = client.get(reverse('signin'))

    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)
    assert 'Вход' in response.context['page_title']


@pytest.mark.integration
@pytest.mark.django_db
def test_signin_view_authenticated_user_redirect(client: Any, django_user_model: Any) -> None:
    """Тест что авторизованный пользователь перенаправляется со страницы входа"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    response = client.get(reverse('signin'))

    assert response.status_code == 302
    assert response.url == reverse('city-all-list')


@pytest.mark.integration
@pytest.mark.django_db
def test_signin_view_post_valid_credentials(client: Any, django_user_model: Any) -> None:
    """Тест успешной авторизации"""
    django_user_model.objects.create_user(username='testuser', password='password123')

    response = client.post(
        reverse('signin'), data={'username': 'testuser', 'password': 'password123'}, follow=True
    )

    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.username == 'testuser'


@pytest.mark.integration
@pytest.mark.django_db
def test_signin_view_post_invalid_credentials(client: Any, django_user_model: Any) -> None:
    """Тест авторизации с неверными учётными данными"""
    django_user_model.objects.create_user(username='testuser', password='password123')

    response = client.post(
        reverse('signin'), data={'username': 'testuser', 'password': 'wrongpassword'}
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert 'form' in response.context
    assert response.context['form'].errors


@pytest.mark.integration
@pytest.mark.django_db
def test_signin_view_post_nonexistent_user(client: Any) -> None:
    """Тест авторизации несуществующего пользователя"""
    response = client.post(
        reverse('signin'), data={'username': 'nonexistent', 'password': 'password123'}
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


# ===== Тесты для signup_success =====


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.access.logger_email')
def test_signup_success_view(mock_logger: Any, client: Any, django_user_model: Any) -> None:
    """Тест страницы успешной регистрации через реальную регистрацию"""
    # Регистрируем пользователя
    signup_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'TestPass123!',
        'password2': 'TestPass123!',
        'personal_data_consent': True,
        'personal_data_version': '1.0',
    }
    response = client.post(reverse('signup'), data=signup_data)

    # Проверяем, что перенаправляет на список городов (успешная регистрация)
    assert response.status_code == 302


# ===== Тесты для MyPasswordChangeView =====


@pytest.mark.integration
@pytest.mark.django_db
def test_password_change_view_get_request(client: Any, django_user_model: Any) -> None:
    """Тест GET запроса на страницу изменения пароля"""
    user = django_user_model.objects.create_user(username='testuser', password='oldpassword123')
    client.force_login(user)

    response = client.get(reverse('password_change_form'))

    assert response.status_code == 200
    assert 'account/profile__password_change_form.html' in (t.name for t in response.templates)
    assert 'Изменение пароля' in response.context['page_title']


@pytest.mark.integration
@pytest.mark.django_db
def test_password_change_view_unauthenticated(client: Any) -> None:
    """Тест что неавторизованный пользователь перенаправляется"""
    response = client.get(reverse('password_change_form'))

    assert response.status_code == 302
    assert response.url.startswith('/account/signin')


@pytest.mark.integration
@pytest.mark.django_db
def test_password_change_view_post_valid_data(client: Any, django_user_model: Any) -> None:
    """Тест успешного изменения пароля"""
    user = django_user_model.objects.create_user(username='testuser', password='oldpassword123')
    client.force_login(user)

    response = client.post(
        reverse('password_change_form'),
        data={
            'old_password': 'oldpassword123',
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!',
        },
        follow=True,
    )

    assert response.status_code == 200

    # Проверяем, что пароль действительно изменился
    user.refresh_from_db()
    assert user.check_password('NewPassword123!')


@pytest.mark.integration
@pytest.mark.django_db
def test_password_change_view_post_invalid_old_password(client: Any, django_user_model: Any) -> None:
    """Тест изменения пароля с неверным старым паролем"""
    user = django_user_model.objects.create_user(username='testuser', password='oldpassword123')
    client.force_login(user)

    response = client.post(
        reverse('password_change_form'),
        data={
            'old_password': 'wrongoldpassword',
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!',
        },
    )

    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors

    # Проверяем, что пароль не изменился
    user.refresh_from_db()
    assert user.check_password('oldpassword123')


# ===== Тесты для MyPasswordResetDoneView =====


@pytest.mark.integration
@pytest.mark.django_db
def test_password_change_done_view(client: Any, django_user_model: Any) -> None:
    """Тест страницы успешного изменения пароля"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    response = client.get(reverse('password_change_done'))

    assert response.status_code == 200
    assert 'account/profile__password_change_done.html' in (t.name for t in response.templates)
    assert 'Изменение пароля' in response.context['page_title']


@pytest.mark.integration
@pytest.mark.django_db
def test_password_change_done_view_unauthenticated(client: Any) -> None:
    """Тест что неавторизованный пользователь не может просмотреть страницу"""
    response = client.get(reverse('password_change_done'))

    assert response.status_code == 302


# ===== Тесты для password reset flow =====


@pytest.mark.integration
@pytest.mark.django_db
def test_password_reset_view_get_request(client: Any) -> None:
    """Тест GET запроса на страницу восстановления пароля"""
    response = client.get(reverse('reset_password'))

    assert response.status_code == 200
    assert 'account/profile__password_reset__form.html' in (t.name for t in response.templates)


@pytest.mark.integration
@pytest.mark.django_db
def test_password_reset_view_post_valid_email(client: Any, django_user_model: Any) -> None:
    """Тест отправки письма для восстановления пароля"""
    django_user_model.objects.create_user(
        username='testuser', email='test@example.com', password='password123'
    )

    response = client.post(reverse('reset_password'), data={'email': 'test@example.com'})

    assert response.status_code == 302
    assert response.url == reverse('password_reset_done')


@pytest.mark.integration
@pytest.mark.django_db
def test_password_reset_done_view(client: Any) -> None:
    """Тест страницы после отправки письма для восстановления пароля"""
    response = client.get(reverse('password_reset_done'))

    assert response.status_code == 200
    assert 'account/profile__password_reset__email_sent.html' in (
        t.name for t in response.templates
    )


# ===== Тесты для logout =====


@pytest.mark.integration
@pytest.mark.django_db
def test_logout_view(client: Any, django_user_model: Any) -> None:
    """Тест выхода из системы"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    assert client.session.get('_auth_user_id')

    response = client.post(reverse('logout'), follow=True)

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
