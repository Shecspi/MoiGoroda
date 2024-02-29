

import pytest
from django.urls import reverse


def create_user(user_id: int, django_user_model):
    return django_user_model.objects.create_user(id=user_id, username=f'username{user_id}', password='password')


def create_superuser(django_user_model):
    return django_user_model.objects.create_user(id=1, username='superuser', password='password', is_superuser=True)


@pytest.fixture
def setup(client, django_user_model):
    user1 = create_user(1, django_user_model)
    user2 = create_user(2, django_user_model)
    superuser = create_superuser(django_user_model)


@pytest.mark.django_db
def test__access__not_existing_user__guest(client):
    """
    При попытке просмотра статистики неуществующего пользователя должна возвращаться ошибка 404.
    """
    response = client.get(reverse('share', kwargs={'pk': 999}))
    assert response.status_code == 404


@pytest.mark.django_db
def test__access__not_existing_user__auth_user(client):
    """
    При попытке просмотра статистики неуществующего пользователя должна возвращаться ошибка 404.
    """
    client.login(username='username', password='password')
    response = client.get(reverse('share', kwargs={'pk': 999}))
    assert response.status_code == 404


@pytest.mark.django_db
def test__access__not_existing_user__superuser(client):
    """
    При попытке просмотра статистики неуществующего пользователя должна возвращаться ошибка 404.
    """
    client.login(username='superuser', password='password')
    response = client.get(reverse('share', kwargs={'pk': 999}))
    assert response.status_code == 404


@pytest.mark.django_db
def test__access__has_no_permissions__existing_user__guest(setup, client):
    """
    Если пользователь ни разу не применял настройки "Поделиться статистикой",
    то по-умолчанию его статистика не доступна к просмотру авторизованным пользователям.
    """
    response = client.get(reverse('share', kwargs={'pk': 2}))
    assert response.status_code == 404


@pytest.mark.django_db
def test__access__has_no_permissions__existing_user__auth_user(setup, client):
    """
    Если пользователь ни разу не применял настройки "Поделиться статистикой",
    то по-умолчанию его статистика не доступна к просмотру авторизованным пользователям.
    """
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 2}))
    assert response.status_code == 404


@pytest.mark.django_db
def test__access__has_no_permissions__existing_user__superuser(setup, client):
    """
    Если пользователь ни разу не применял настройки "Поделиться статистикой",
    то его статистика доступна к просмотру супер-пользователям.
    """
    client.login(username='superuser', password='password')
    response = client.get(reverse('share', kwargs={'pk': 2}))
    assert response.status_code == 200


@pytest.mark.django_db
def test__access__has_no_permissions__existing_user__self(setup, client):
    """
    При просмотре своей статистики действуют те же ограничения, что и для всех.
    Если записи в БД нет, то и доступа к этой статистике нет
    """
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    assert response.status_code == 404
