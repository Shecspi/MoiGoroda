from datetime import datetime

import pytest
from bs4 import BeautifulSoup

from django.urls import reverse

from tests.account.download.create_db import (
    create_user,
    create_area,
    create_region,
    create_city,
    create_visited_city,
)


@pytest.fixture
def setup_db(django_user_model):
    user = create_user(django_user_model, 1)
    area = create_area(1)
    region = create_region(1, area[0])
    city = create_city(2, region[0])
    date_of_visit_1 = datetime.strptime('2024-01-01', '%Y-%m-%d')
    date_of_visit_2 = datetime.strptime('2023-01-01', '%Y-%m-%d')
    create_visited_city(region[0], user, city[0], date_of_visit_1, False, 3)
    create_visited_city(region[0], user, city[1], date_of_visit_2, True, 5)


@pytest.mark.django_db
def test__statistics_page_has_download_button(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('stats'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    button = content.find('button', {'id': 'download_button'})

    assert button
    assert button.find('i', {'class': 'fa-solid fa-download'})
    assert 'Скачать' in button.get_text()


@pytest.mark.django_db
def test__statistics_page_has_download_modal_window(setup_db, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('stats'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    modal = content.find('div', {'id': 'download_modal'})

    assert modal
