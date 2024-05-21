"""
Тестирует корректность отображения контента на странице детальной информации о посещённом городе.
Страница тестирования '/city/<pk>'.

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
from collection.models import Collection
from region.models import Area, Region


@pytest.fixture
def setup_db__detail__data_exists(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    city = City.objects.create(
        title=f'Город 1',
        region=region,
        population=5000,
        date_of_foundation=1990,
        coordinate_width=1,
        coordinate_longitude=1,
        wiki='https://wiki.ru/Город_1',
    )
    VisitedCity.objects.create(
        id=1,
        user=user,
        region=region,
        city=city,
        date_of_visit=f'2023-01-01',
        has_magnet=True,
        impression='Хороший город',
        rating=3,
    )
    # Collection.objects.create(id=1, title='Коллекция 1', city=city)
    # Collection.objects.create(id=1, title='Коллекция 2', city=city)


@pytest.fixture
def setup_db__detail__data_not_exists(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(area=area, title='Регион 1', type='область', iso3166='RU-RU1')
    city = City.objects.create(
        title=f'Город 1', region=region, coordinate_width=1, coordinate_longitude=1
    )
    VisitedCity.objects.create(
        id=1, user=user, region=region, city=city, has_magnet=False, rating=3
    )


@pytest.mark.django_db
def test__content(setup_db__detail__data_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    page_header = content.find('h1', {'id': 'section-page_header'})

    assert page_header
    assert 'Город 1' in page_header.get_text()


@pytest.mark.django_db
def test__section_region(setup_db__detail__data_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-region'})

    assert section
    assert 'Регион:' in section.find('div', {'id': 'subsection-region_title'}).get_text()
    assert 'Регион 1 область' in section.find('div', {'id': 'subsection-region_value'}).get_text()


@pytest.mark.django_db
def test__section_area(setup_db__detail__data_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-area'})

    assert section
    assert 'Федеральный округ:' in section.find('div', {'id': 'subsection-area_title'}).get_text()
    assert 'Округ 1' in section.find('div', {'id': 'subsection-area_value'}).get_text()


@pytest.mark.django_db
def test__section_date_of_foundation_exists(setup_db__detail__data_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-date_of_foundation'})

    assert section
    assert (
        'Год основания:'
        in section.find('div', {'id': 'subsection-date_of_foundation_title'}).get_text()
    )
    assert '1990' in section.find('div', {'id': 'subsection-date_of_foundation_value'}).get_text()


@pytest.mark.django_db
def test__section_date_of_foundation_not_exists(setup_db__detail__data_not_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-date_of_foundation'})

    assert section
    assert (
        'Год основания:'
        in section.find('div', {'id': 'subsection-date_of_foundation_title'}).get_text()
    )
    assert (
        'Год основания не известен'
        in section.find('div', {'id': 'subsection-date_of_foundation_value'}).get_text()
    )


@pytest.mark.django_db
def test__section_population_exists(setup_db__detail__data_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-population'})

    assert section
    assert 'Население:' in section.find('div', {'id': 'subsection-population_title'}).get_text()
    assert '5\xa0000 чел.' in section.find('div', {'id': 'subsection-population_value'}).get_text()


@pytest.mark.django_db
def test__section_population_not_exists(setup_db__detail__data_not_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-population'})

    assert section
    assert 'Население:' in section.find('div', {'id': 'subsection-population_title'}).get_text()
    assert (
        'Численность населения не известна'
        in section.find('div', {'id': 'subsection-population_value'}).get_text()
    )


@pytest.mark.django_db
def test__section_collectins_not_exists(setup_db__detail__data_not_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-collections'})

    assert section
    assert 'Коллекции:' in section.find('div', {'id': 'subsection-collections_title'}).get_text()
    assert (
        'Город не состоит ни в каких коллекциях'
        in section.find('div', {'id': 'subsection-collections_value'}).get_text()
    )


@pytest.mark.django_db
def test__section_date_of_visit_exists(setup_db__detail__data_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-date_of_visit'})

    assert section
    assert (
        'Дата посещения:'
        in section.find('div', {'id': 'subsection-date_of_visit_title'}).get_text()
    )
    assert (
        '1 января 2023 г.'
        in section.find('div', {'id': 'subsection-date_of_visit_value'}).get_text()
    )


@pytest.mark.django_db
def test__section_population_not_exists(setup_db__detail__data_not_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-date_of_visit'})

    assert section
    assert (
        'Дата посещения:'
        in section.find('div', {'id': 'subsection-date_of_visit_title'}).get_text()
    )
    assert (
        'Дата посещения не указана'
        in section.find('div', {'id': 'subsection-date_of_visit_value'}).get_text()
    )


@pytest.mark.django_db
def test__section_has_magnet_exists(setup_db__detail__data_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-has_magnet'})

    assert section
    assert (
        'Сувенир из города:'
        in section.find('div', {'id': 'subsection-has_magnet_title'}).get_text()
    )
    assert (
        'имеется'
        in section.find('div', {'id': 'subsection-has_magnet_value'})
        .find('span', {'class': 'badge bg-success'})
        .get_text()
    )


@pytest.mark.django_db
def test__section_has_magnet_not_exists(setup_db__detail__data_not_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-has_magnet'})

    assert section
    assert (
        'Сувенир из города:'
        in section.find('div', {'id': 'subsection-has_magnet_title'}).get_text()
    )
    assert (
        'отсутствует'
        in section.find('div', {'id': 'subsection-has_magnet_value'})
        .find('span', {'class': 'badge bg-danger'})
        .get_text()
    )


@pytest.mark.django_db
def test__section_impression(setup_db__detail__data_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-impression'})

    assert section
    assert 'Впечатления:' in section.find('div', {'id': 'subsection-impression_title'}).get_text()
    assert 'Хороший город' in section.find('div', {'id': 'subsection-impression_value'}).get_text()


@pytest.mark.django_db
def test__section_rating(setup_db__detail__data_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    section = content.find('div', {'id': 'section-rating'})

    assert section
    assert 'Ваша оценка:' in section.find('div', {'id': 'subsection-rating_title'}).get_text()
    assert (
        len(
            section.find('div', {'id': 'subsection-rating_value'}).find_all(
                'i', {'class': 'fa-solid fa-star'}
            )
        )
        == 3
    )
    assert (
        len(
            section.find('div', {'id': 'subsection-rating_value'}).find_all(
                'i', {'class': 'fa-regular fa-star'}
            )
        )
        == 2
    )


@pytest.mark.django_db
def test__buttons(setup_db__detail__data_exists, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    link_wiki = content.find('a', {'id': 'link-wiki', 'href': 'https://wiki.ru/Город_1'})
    link_update = content.find(
        'a', {'id': 'link-update', 'href': reverse('city-update', kwargs={'pk': 1})}
    )
    link_delete = content.find('button', {'id': 'link-delete'})

    assert link_wiki
    assert link_wiki.find('i', {'class': 'fa-brands fa-wikipedia-w'})
    assert 'Wikipedia' in link_wiki.get_text()
    assert link_update
    assert link_update.find('i', {'class': 'fa-regular fa-pen-to-square'})
    assert 'Изменить' in link_update.get_text()
    assert link_delete
    assert link_delete.find('i', {'class': 'fa-solid fa-trash-can'})
    assert 'Удалить' in link_delete.get_text()
