import pytest

from bs4 import BeautifulSoup
from django.urls import reverse

from tests.subscribe.conftest import create_permissions_in_db, create_subscription


@pytest.mark.django_db
def not_auth_user_cant_see_subscription_button__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, True))

    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})

    assert not content.find('button', {'id': 'subscribe'})


@pytest.mark.django_db
def auth_user_cant_see_subscription_button_if_it_is_not_allow__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, False))

    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})

    assert not content.find('button', {'id': 'subscribe'})


@pytest.mark.django_db
def auth_user_can_see_subscription_button__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, True))

    client.login(username='username2', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})

    button = content.find('button', {'id': 'subscribe'})
    assert button
    assert button.find('i', {'class': 'fa-solid fa-bell'})
    assert 'Подписаться' in button.get_text()


@pytest.mark.django_db
def auth_user_can_see_unsubscription_button_if_already_subscribe__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, True))
    create_subscription(2, 1)

    client.login(username='username2', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})

    button = content.find('button', {'id': 'subscribe'})
    assert button
    assert button.find('i', {'class': 'fa-regular fa-bell'})
    assert 'Отписаться' in button.get_text()


@pytest.mark.django_db
def superuser_can_see_subscription_button__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, True))

    client.login(username='superuser3', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})

    button = content.find('button', {'id': 'subscribe'})
    assert button
    assert button.find('i', {'class': 'fa-solid fa-bell'})
    assert 'Подписаться' in button.get_text()


@pytest.mark.django_db
def superuser_can_see_subscription_button_even_it_is_not_allow__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, False))

    client.login(username='superuser3', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})

    button = content.find('button', {'id': 'subscribe'})
    assert button
    assert button.find('i', {'class': 'fa-solid fa-bell'})
    assert 'Подписаться' in button.get_text()


@pytest.mark.django_db
def superuser_can_see_unsubscription_button_if_already_subscribe__test(setup, client):
    create_permissions_in_db(1, (True, True, True, True, True))
    create_subscription(3, 1)

    client.login(username='superuser3', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})

    button = content.find('button', {'id': 'subscribe'})
    assert button
    assert button.find('i', {'class': 'fa-regular fa-bell'})
    assert 'Отписаться' in button.get_text()
