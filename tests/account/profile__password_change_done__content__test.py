"""
Тестирует наличие всех необходимомых элементов страницы.
Страница тестирования '/account/password/change/done'.

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
def test__content__main_parts(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('password_change_done'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    header = content.find('h1', {'id': 'change_password-section-page_header'})

    assert header
    assert header.find(string='Изменение пароля')
    assert source.find('div', {'id': 'sidebar'})
    assert content
    assert source.find('footer', {'id': 'section-footer'})


@pytest.mark.django_db
def test__content__alert(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('password_change_done'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    alert = content.find('div', {'id': 'change_password-alert'})

    assert alert
    assert alert.find(string='Ваш пароль успешно изменён')
