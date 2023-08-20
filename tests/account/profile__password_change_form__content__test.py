"""
Тестирует наличие всех необходимомых элементов страницы.
Страница тестирования '/account/password/change/'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from bs4 import BeautifulSoup

from django.urls import reverse


@pytest.fixture
def setup_db(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')


@pytest.mark.django_db
def test__content__section__content(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('password_change_form'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    card = content.find('div', {'id': 'change_password-section-card'})
    header = content.find('h1', {'id': 'change_password-section-page_header'})

    assert header
    assert header.find(string='Изменение пароля')
    assert source.find('div', {'id': 'sidebar'})
    assert content
    assert card
    assert source.find('footer', {'id': 'section-footer'})


@pytest.mark.django_db
def test__content__subection__old_password(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('password_change_form'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    card = content.find('div', {'id': 'change_password-section-card'})
    old_password = card.find('div', {'id': 'div_id_old_password'})

    assert old_password
    assert 'Старый пароль' in old_password.find('label').get_text()
    assert old_password.find('input', {'type': 'password', 'required': True})


@pytest.mark.django_db
def test__content__subection__new_password1(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('password_change_form'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    card = content.find('div', {'id': 'change_password-section-card'})
    new_password = card.find('div', {'id': 'div_id_new_password1'})

    assert new_password
    assert 'Новый пароль' in new_password.find('label').get_text()
    assert new_password.find('input', {'type': 'password', 'required': True})


@pytest.mark.django_db
def test__content__subection__new_password2(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('password_change_form'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    card = content.find('div', {'id': 'change_password-section-card'})
    new_password = card.find('div', {'id': 'div_id_new_password2'})

    assert new_password
    assert 'Подтверждение нового пароля' in new_password.find('label').get_text()
    assert new_password.find('input', {'type': 'password', 'required': True})


@pytest.mark.django_db
def test__content__button__submit(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('password_change_form'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    card = content.find('div', {'id': 'change_password-section-card'})
    button = card.find('button', {'type': 'submit'})

    assert button
    assert button(string='Изменить пароль')
