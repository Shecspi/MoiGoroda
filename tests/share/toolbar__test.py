import pytest

from bs4 import BeautifulSoup
from django.urls import reverse

from tests.create_db import (
    create_share_settings,
    create_user,
    create_superuser,
    create_subscription,
)


@pytest.fixture
def setup_db(django_user_model):
    create_user(django_user_model, 1)
    create_user(django_user_model, 2)
    create_superuser(django_user_model, 3)


@pytest.mark.django_db
def page_has_no_toolbar_for_guest__test(setup_db, client):
    create_share_settings(1)

    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    toolbar = content.find('div', {'id': 'toolbar'})

    assert not toolbar


@pytest.mark.django_db
def page_has_toolbar_for_auth_user_if_has_permission_to_subscribe__test(setup_db, client):
    create_share_settings(1)

    client.login(username='username2', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    toolbar = content.find('div', {'id': 'toolbar'})

    assert toolbar


@pytest.mark.django_db
def page_has_no_toolbar_for_auth_user_if_has_no_permission_to_subscribe__test(setup_db, client):
    create_share_settings(1, can_subscribe=False)

    client.login(username='username2', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    toolbar = content.find('div', {'id': 'toolbar'})

    assert not toolbar


@pytest.mark.django_db
def page_has_no_toolbar_for_auth_user_if_user_visit_himself__test(setup_db, client):
    create_share_settings(1)

    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    toolbar = content.find('div', {'id': 'toolbar'})

    assert not toolbar


@pytest.mark.django_db
def page_has_toolbar_for_superuser_if_has_permission_to_subscribe__test(setup_db, client):
    create_share_settings(1)

    client.login(username='superuser3', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    toolbar = content.find('div', {'id': 'toolbar'})

    assert toolbar


@pytest.mark.django_db
def page_has_toolbar_for_superuser_if_has_no_permission_to_subscribe__test(setup_db, client):
    client.login(username='superuser3', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    toolbar = content.find('div', {'id': 'toolbar'})

    assert toolbar


@pytest.mark.django_db
def page_has_no_toolbar_for_superuser_if_superuser_visit_himself__test(setup_db, client):
    create_share_settings(1)

    client.login(username='superuser3', password='password')
    response = client.get(reverse('share', kwargs={'pk': 3}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    toolbar = content.find('div', {'id': 'toolbar'})

    assert not toolbar


@pytest.mark.django_db
def test__page_has_disabled_subscription_button_for_auth_user_if_user_has_no_subscription__test(
    setup_db, client
):
    """
    Если подписка на пользователя ещё не оформлена, то должна отображаться кнопка "Подписаться".
    А кнопка "Отписаться" должна быть скрыта.
    """
    create_share_settings(1)

    client.login(username='username2', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    toolbar = content.find('div', {'id': 'toolbar'})
    subscribe_button = toolbar.find(
        'button', {'id': 'subscribe_button', 'class': 'btn btn-outline-success', 'hidden': False}
    )
    unsubscribe_button = toolbar.find(
        'button', {'id': 'unsubscribe_button', 'class': 'btn btn-success', 'hidden': True}
    )

    assert subscribe_button
    assert 'Подписаться' in subscribe_button.get_text()
    assert unsubscribe_button


@pytest.mark.django_db
def test__page_has_enabled_subscription_button_for_auth_user_if_user_has_no_subscription__test(
    setup_db, client
):
    """
    Если подписка на пользователя оформлена, то должна отображаться кнопка "Отписаться".
    А кнопка "Подписаться" должна быть скрыта.
    """
    create_share_settings(1)
    create_subscription(2, 1)

    client.login(username='username2', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    toolbar = content.find('div', {'id': 'toolbar'})
    subscribe_button = toolbar.find(
        'button', {'id': 'subscribe_button', 'class': 'btn btn-outline-success', 'hidden': True}
    )
    unsubscribe_button = toolbar.find(
        'button', {'id': 'unsubscribe_button', 'class': 'btn btn-success', 'hidden': False}
    )

    assert subscribe_button
    assert unsubscribe_button
    assert 'Отписаться' in unsubscribe_button.get_text()
