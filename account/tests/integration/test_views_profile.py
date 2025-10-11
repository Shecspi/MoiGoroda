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

from account.models import ShareSettings
from subscribe.infrastructure.models import Subscribe


# ===== Фикстуры =====


@pytest.fixture
def create_test_user(django_user_model):
    """Создаёт тестового пользователя"""
    return django_user_model.objects.create_user(
        username='testuser', email='test@example.com', password='password123'
    )


@pytest.fixture
def create_multiple_users(django_user_model):
    """Создаёт несколько тестовых пользователей"""
    user1 = django_user_model.objects.create_user(
        username='user1', email='user1@test.com', password='password123'
    )
    user2 = django_user_model.objects.create_user(
        username='user2', email='user2@test.com', password='password123'
    )
    user3 = django_user_model.objects.create_user(
        username='user3', email='user3@test.com', password='password123'
    )
    return {'user1': user1, 'user2': user2, 'user3': user3}


# ===== Тесты для Profile View =====


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_get_request_authenticated(client, create_test_user):
    """Тест GET запроса на страницу профиля для авторизованного пользователя"""
    client.force_login(create_test_user)
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    assert 'account/profile.html' in (t.name for t in response.templates)
    assert 'Профиль' in response.context['page_title']


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_get_request_unauthenticated(client):
    """Тест что неавторизованный пользователь перенаправляется"""
    response = client.get(reverse('profile'))

    assert response.status_code == 302
    assert response.url.startswith('/account/signin')


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_displays_user_data(client, create_test_user):
    """Тест что страница профиля отображает данные пользователя"""
    create_test_user.first_name = 'John'
    create_test_user.last_name = 'Doe'
    create_test_user.save()

    client.force_login(create_test_user)
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    assert 'form' in response.context
    form = response.context['form']
    assert form.initial['username'] == 'testuser'
    assert form.initial['email'] == 'test@example.com'
    assert form.initial['first_name'] == 'John'
    assert form.initial['last_name'] == 'Doe'


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.profile.logger')
def test_profile_view_post_valid_data(mock_logger, client, create_test_user):
    """Тест успешного обновления профиля"""
    client.force_login(create_test_user)

    updated_data = {
        'username': 'updateduser',
        'email': 'updated@example.com',
        'first_name': 'Jane',
        'last_name': 'Smith',
    }

    response = client.post(reverse('profile'), data=updated_data, follow=True)

    assert response.status_code == 200

    # Проверяем, что данные обновились
    create_test_user.refresh_from_db()
    assert create_test_user.username == 'updateduser'
    assert create_test_user.email == 'updated@example.com'
    assert create_test_user.first_name == 'Jane'
    assert create_test_user.last_name == 'Smith'

    # Проверяем, что логирование произошло
    mock_logger.info.assert_called_once()


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_post_invalid_data(client, create_test_user):
    """Тест обновления профиля с невалидными данными"""
    client.force_login(create_test_user)

    invalid_data = {'username': '', 'email': 'invalid-email', 'first_name': '', 'last_name': ''}

    response = client.post(reverse('profile'), data=invalid_data)

    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors

    # Проверяем, что данные не изменились
    create_test_user.refresh_from_db()
    assert create_test_user.username == 'testuser'
    assert create_test_user.email == 'test@example.com'


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_shows_subscribed_users(client, create_multiple_users):
    """Тест что страница профиля показывает подписки пользователя"""
    users = create_multiple_users

    # user1 подписывается на user2 и user3
    Subscribe.objects.create(subscribe_from=users['user1'], subscribe_to=users['user2'])
    Subscribe.objects.create(subscribe_from=users['user1'], subscribe_to=users['user3'])

    client.force_login(users['user1'])
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    assert 'subscribed_users' in response.context
    assert len(response.context['subscribed_users']) == 2
    assert response.context['number_of_subscribed_users'] == 2

    usernames = {user.username for user in response.context['subscribed_users']}
    assert 'user2' in usernames
    assert 'user3' in usernames


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_shows_subscriber_users(client, create_multiple_users):
    """Тест что страница профиля показывает подписчиков пользователя"""
    users = create_multiple_users

    # user2 и user3 подписываются на user1
    Subscribe.objects.create(subscribe_from=users['user2'], subscribe_to=users['user1'])
    Subscribe.objects.create(subscribe_from=users['user3'], subscribe_to=users['user1'])

    client.force_login(users['user1'])
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    assert 'subscriber_users' in response.context
    assert len(response.context['subscriber_users']) == 2
    assert response.context['number_of_subscriber_users'] == 2

    usernames = {user.username for user in response.context['subscriber_users']}
    assert 'user2' in usernames
    assert 'user3' in usernames


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_no_subscriptions(client, create_test_user):
    """Тест что страница профиля корректно отображается без подписок"""
    client.force_login(create_test_user)
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    assert response.context['number_of_subscribed_users'] == 0
    assert response.context['number_of_subscriber_users'] == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_context_data(client, create_test_user):
    """Тест наличия необходимых данных в контексте"""
    client.force_login(create_test_user)
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    assert 'active_page' in response.context
    assert response.context['active_page'] == 'profile'
    assert 'page_title' in response.context
    assert 'page_description' in response.context


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_post_with_only_required_fields(client, create_test_user):
    """Тест обновления профиля с только обязательными полями"""
    client.force_login(create_test_user)

    data = {
        'username': 'newusername',
        'email': 'new@example.com',
        'first_name': '',
        'last_name': '',
    }

    response = client.post(reverse('profile'), data=data, follow=True)

    assert response.status_code == 200
    create_test_user.refresh_from_db()
    assert create_test_user.username == 'newusername'
    assert create_test_user.email == 'new@example.com'
    assert create_test_user.first_name == ''
    assert create_test_user.last_name == ''


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_post_duplicate_username(client, create_multiple_users):
    """Тест обновления профиля с уже существующим username"""
    users = create_multiple_users
    client.force_login(users['user1'])

    # Пытаемся изменить username на уже существующий
    data = {
        'username': 'user2',  # Этот username уже занят user2
        'email': 'user1@test.com',
        'first_name': '',
        'last_name': '',
    }

    response = client.post(reverse('profile'), data=data)

    # В Django стандартная форма User не проверяет уникальность username при обновлении
    # если это тот же пользователь, но проверяет если это другой пользователь
    # Поэтому мы должны ожидать ошибку
    assert response.status_code == 200

    # Проверяем, что username не изменился
    users['user1'].refresh_from_db()
    assert users['user1'].username == 'user1'


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_subscriber_with_share_settings(client, create_multiple_users):
    """Тест отображения can_subscribe для подписчиков с настройками публикации"""
    users = create_multiple_users

    # user2 подписывается на user1
    Subscribe.objects.create(subscribe_from=users['user2'], subscribe_to=users['user1'])

    # Создаём ShareSettings для user2 с can_share=True
    ShareSettings.objects.create(user=users['user2'], can_share=True)

    client.force_login(users['user1'])
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    subscriber = response.context['subscriber_users'][0]
    assert subscriber.can_subscribe is True


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_success_url_redirect(client, create_test_user):
    """Тест редиректа после успешного обновления профиля"""
    client.force_login(create_test_user)

    data = {
        'username': 'newusername',
        'email': 'new@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
    }

    response = client.post(reverse('profile'), data=data)

    assert response.status_code == 302
    assert response.url == reverse('profile')


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_get_object_uses_session_user(client, create_multiple_users):
    """Тест что Profile использует пользователя из сессии, а не из URL"""
    users = create_multiple_users
    client.force_login(users['user1'])

    # Запрашиваем профиль без указания ID в URL
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    # Проверяем, что отображается профиль user1, а не другого пользователя
    form = response.context['form']
    assert form.initial['username'] == 'user1'


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_form_helper_present(client, create_test_user):
    """Тест наличия crispy form helper"""
    client.force_login(create_test_user)
    response = client.get(reverse('profile'))

    assert response.status_code == 200
    form = response.context['form']
    assert hasattr(form, 'helper')


@pytest.mark.integration
@pytest.mark.django_db
def test_profile_view_preserves_password(client, create_test_user):
    """Тест что обновление профиля не изменяет пароль"""
    client.force_login(create_test_user)
    original_password = create_test_user.password

    data = {
        'username': 'newusername',
        'email': 'new@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
    }

    client.post(reverse('profile'), data=data)

    create_test_user.refresh_from_db()
    assert create_test_user.password == original_password
