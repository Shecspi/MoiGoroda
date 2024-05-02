from datetime import datetime

import pytest
from django.urls import reverse

from tests.account.download.create_db import create_user, create_area, create_region, create_city, create_visited_city


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
def test__access_by_get_for_guest_is_prohibited(client):
    response = client.get(reverse('download'))
    assert response.status_code == 405


@pytest.mark.django_db
def test__access_by_get_for_auth_user_is_prohibited(django_user_model, client):
    create_user(django_user_model, 1)

    client.login(username='username1', password='password')
    response = client.get(reverse('download'))

    assert response.status_code == 405


@pytest.mark.django_db
def test__access_by_post_for_guest_is_prohibited(client):
    response = client.post(reverse('download'))
    assert response.status_code == 302

    response = client.post(reverse('download'), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__access_by_post_for_auth_user_is_allowed(django_user_model, client):
    create_user(django_user_model, 1)

    client.login(username='username1', password='password')
    data = {
        'reporttype': 'city',
        'filetype': 'txt'
    }
    response = client.post(reverse('download'), data=data)

    assert response.status_code == 200
    assert response.content.decode() == ('Город     Регион     Дата посещения     '
                                         'Наличие магнита     Оценка     \n')


@pytest.mark.django_db
def test__content_of_city_report_in_txt_file(setup_db, client):
    client.login(username='username1', password='password')
    data = {
        'reporttype': 'city',
        'filetype': 'txt'
    }
    response = client.post(reverse('download'), data=data)
    report = response.content.decode().split('\n')

    assert report[0] == 'Город       Регион               Дата посещения     Наличие магнита     Оценка     '
    assert report[1] == 'Город 1     Регион 1 область     2024-01-01         -                   ***        '
    assert report[2] == 'Город 2     Регион 1 область     2023-01-01         +                   *****      '


@pytest.mark.django_db
def test__content_of_region_report_in_txt_file(setup_db, client):
    client.login(username='username1', password='password')
    data = {
        'reporttype': 'region',
        'filetype': 'txt'
    }
    response = client.post(reverse('download'), data=data)
    report = response.content.decode().split('\n')

    assert report[0] == ('Регион               Всего городов     Посещено городов, шт     '
                         'Посещено городов, %     Осталось посетить, шт     ')
    assert report[1] == ('Регион 1 область     2                 2                        '
                         '100%                    0                         ')


@pytest.mark.django_db
def test__content_of_area_report_in_txt_file(setup_db, client):
    client.login(username='username1', password='password')
    data = {
        'reporttype': 'area',
        'filetype': 'txt'
    }
    response = client.post(reverse('download'), data=data)
    report = response.content.decode().split('\n')

    assert report[0] == ('Федеральный округ     Всего регионов, шт     Посещено регионов, шт     '
                         'Посещено регионов, %     Осталось посетить, шт     ')
    assert report[1] == ('Округ 1               1                      1                         '
                         '100%                     0                         ')
