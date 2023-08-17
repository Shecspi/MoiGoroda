"""
Тестирует корректность отображения контента с карточками посещённых городоов.
Страница тестирования '/city/all/list'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from datetime import datetime

from bs4 import BeautifulSoup
from django.urls import reverse

from city.models import City, VisitedCity
from region.models import Area, Region


@pytest.fixture
def setup_db__content_for_pagination(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    for num in range(1, 40):
        city = City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)
        VisitedCity.objects.create(
            user=user, region=region, city=city,
            date_of_visit=f"{datetime.now().year - num}-01-01", has_magnet=False, rating=3
        )


@pytest.fixture
def setup_db__content_for_checking_of_cards__minimum_content(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    for num in range(1, 3):
        city = City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)
        VisitedCity.objects.create(
            user=user, region=region, city=city, has_magnet=False, rating=3
        )


@pytest.fixture
def setup_db__content_for_checking_of_cards__no_content(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    for num in range(1, 3):
        city = City.objects.create(title=f'Город {num}', region=region, coordinate_width=1, coordinate_longitude=1)


@pytest.fixture
def setup_db__content_for_checking_of_cards__maximum_content(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    for num in range(1, 3):
        city = City.objects.create(
            title=f'Город {num}', region=region, population=5000, date_of_foundation='2020',
            coordinate_width=1, coordinate_longitude=1
        )
        VisitedCity.objects.create(
            user=user, region=region, city=city, has_magnet=False, rating=3
        )


@pytest.mark.django_db
def test__content(setup_db__content_for_pagination, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})

    assert source.find('div', {'id': 'sidebar'})
    assert source.find('div', {'id': 'sidebar'}).find('a', {'href': reverse('city-all-list'), 'class': 'active'})
    assert source.find('h1', {'id': 'section-page_header'})
    assert source.find('footer', {'id': 'section-footer'})
    assert content


@pytest.mark.django_db
def test__info_box__no_content(setup_db__content_for_checking_of_cards__no_content, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})

    assert ('На данный момент Вы не сохранили ни одного посещённого города.'
            in content.find('div', {'id': 'section-info_box'}).get_text())


@pytest.mark.django_db
@pytest.mark.parametrize(
    'num, title, date_of_visit, region, population, date_of_foundation, rating', (
        (1, 'Город 1', 'Дата посещения не указана', 'Регион 1',
         'Население города неизвестно', 'Год основания неизвестен', 3),
        (2, 'Город 2', 'Дата посещения не указана', 'Регион 1',
         'Население города неизвестно', 'Год основания неизвестен', 3)
    )
)
def test__cards__minimum_content(setup_db__content_for_checking_of_cards__minimum_content, client,
                                 num, title, date_of_visit, region, population, date_of_foundation, rating):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    card = content.find('div', {'id': f'section-city_{num}'})

    assert card
    assert title in card.find('h4', {'id': f'subsection-city-title_{num}'}).get_text()
    assert date_of_visit in card.find('div', {'id': f'subsection-city-date_of_visit_{num}'}).get_text()
    assert region in card.find('div', {'id': f'subsection-city-region_{num}'}).get_text()
    assert population in card.find('div', {'id': f'subsection-city-population_{num}'}).get_text()
    assert date_of_foundation in card.find('div', {'id': f'subsection-city-date_of_foundation_{num}'}).get_text()
    assert 3 == len(card.find(
        'div', {'id': f'subsection-city-rating_{num}'}
    ).find_all('i', {'class': 'fa-solid fa-star'}))


@pytest.mark.django_db
@pytest.mark.parametrize(
    'num, title, date_of_visit, region, population, date_of_foundation, rating', (
        (1, 'Город 1', 'Дата посещения не указана', 'Регион 1',
         '5\xa0000', '2020', 3),
        (2, 'Город 2', 'Дата посещения не указана', 'Регион 1',
         '5\xa0000', '2020', 3)
    )
)
def test__cards__maximum_content(setup_db__content_for_checking_of_cards__maximum_content, client,
                                 num, title, date_of_visit, region, population, date_of_foundation, rating):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    card = content.find('div', {'id': f'section-city_{num}'})

    assert card
    assert title in card.find('h4', {'id': f'subsection-city-title_{num}'}).get_text()
    assert date_of_visit in card.find('div', {'id': f'subsection-city-date_of_visit_{num}'}).get_text()
    assert region in card.find('div', {'id': f'subsection-city-region_{num}'}).get_text()
    assert population in card.find('div', {'id': f'subsection-city-population_{num}'}).get_text()
    assert date_of_foundation in card.find('div', {'id': f'subsection-city-date_of_foundation_{num}'}).get_text()
    assert 3 == len(card.find(
        'div', {'id': f'subsection-city-rating_{num}'}
    ).find_all('i', {'class': 'fa-solid fa-star'}))


@pytest.mark.django_db
def test__pagination_first_page(setup_db__content_for_pagination, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'section-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('button', {'id': 'link-to_first_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_prev_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 1 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination_second_page(setup_db__content_for_pagination, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list') + '?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'section-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_next_page', 'class': 'btn-outline-success'})
    assert pagination.find('a', {'id': 'link-to_last_page', 'class': 'btn-outline-success'})
    assert 'Страница 2 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()


@pytest.mark.django_db
def test__pagination_third_page(setup_db__content_for_pagination, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-all-list') + '?page=3')
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    pagination = source.find('div', {'id': 'section-content'}).find('div', {'id': 'block-pagination'})

    assert pagination
    assert pagination.find('a', {'id': 'link-to_first_page', 'class': 'btn-outline-danger'})
    assert pagination.find('a', {'id': 'link-to_prev_page', 'class': 'btn-outline-danger'})
    assert pagination.find('button', {'id': 'link-to_next_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert pagination.find('button', {'id': 'link-to_last_page', 'class': 'btn-outline-secondary', 'disabled': True})
    assert 'Страница 3 из 3' in pagination.find('button', {'id': 'pagination-info'}).get_text()
