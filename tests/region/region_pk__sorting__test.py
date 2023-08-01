"""
Тестирует работу сортировки городов конкретного региона.
Страница тестирования '/region/1'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


import pytest
from datetime import datetime

from city.models import City, VisitedCity
from region.models import Area, Region
from utils.CitiesByRegionMixin import CitiesByRegionMixin

from bs4 import BeautifulSoup
from django.urls import reverse
from django.db.models import OuterRef, Exists, Subquery, DateField


@pytest.fixture
def setup_db__region_pk__sorting(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(id=1, area=area, title='Регион 1', type='область', iso3166='RU-RU')
    cities = (
        ('Город 1', f'{datetime.now().year -2}-01-01', True),
        ('Город 2', f'{datetime.now().year -4}-01-01', True),
        ('Город 3', f'{datetime.now().year - 1}-01-01', True),
        ('Город 4', f'{datetime.now().year - 3}-01-01', False),
        ('Город 5', f'{datetime.now().year - 6}-01-01', False),
        ('Город 6', f'{datetime.now().year - 5}-01-01', False)
    )
    for c in cities:
        city = City.objects.create(title=c[0], region=region, coordinate_width=1, coordinate_longitude=1)
        VisitedCity.objects.create(
            user=user, region=region, city=city, date_of_visit=c[1], has_magnet=c[2], rating=3
        )

    return user



@pytest.mark.django_db
@pytest.mark.parametrize(
    'sort_value, expected_value', [
        ('name_down', ['Город 1', 'Город 2', 'Город 3', 'Город 4', 'Город 5', 'Город 6']),
        ('name_up', ['Город 6', 'Город 5', 'Город 4', 'Город 3', 'Город 2', 'Город 1']),
        ('date_down', ['Город 5', 'Город 6', 'Город 2', 'Город 4', 'Город 1', 'Город 3']),
        ('date_up', ['Город 3', 'Город 1', 'Город 4', 'Город 2', 'Город 6', 'Город 5']),
        ('default_auth', ['Город 3', 'Город 1', 'Город 4', 'Город 2', 'Город 6', 'Город 5']),
        ('default_guest', ['Город 1', 'Город 2', 'Город 3', 'Город 4', 'Город 5', 'Город 6'])
    ]
)
def test__method_apply_sort_to_queryset_correct_value(setup_db__region_pk__sorting, sort_value, expected_value):
    """
    Проверяет корректность работы метода сортировки Queryset - CitiesByRegionMixin.apply_sort_to_queryset().
    Должны отображаться все города региона, как посещённые, так и нет.
    """
    mixin = CitiesByRegionMixin()
    queryset = City.objects.annotate(
        is_visited=Exists(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db__region_pk__sorting)
        ),
        date_of_visit=Subquery(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db__region_pk__sorting).values('date_of_visit'),
            output_field=DateField()
        )
    )

    result = [city for city in mixin.apply_sort_to_queryset(queryset, sort_value).values_list('title', flat=True)]
    assert result == expected_value


def test__method_apply_sort_to_queryset_incorrect_value(setup_db__region_pk__sorting):
    """
    Проверяет корректность работы метода сортировки Queryset - CitiesByRegionMixin.apply_sort_to_queryset().
    При некорректных данных он должен вернуть исключение KeyError.
    """
    mixin = CitiesByRegionMixin()
    queryset = City.objects.annotate(
        is_visited=Exists(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db__region_pk__sorting)
        ),
        date_of_visit=Subquery(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db__region_pk__sorting).values('date_of_visit'),
            output_field=DateField()
        )
    )

    with pytest.raises(KeyError) as info:
        mixin.apply_sort_to_queryset(queryset, 'wrong value').values_list('title', flat=True)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'sort_value, expected_value', [
        ('name_down', ['Город 1', 'Город 2', 'Город 3', 'Город 4']),
        ('name_up', ['Город 4', 'Город 3', 'Город 2', 'Город 1']),
        ('date_down', ['Город 2', 'Город 1', 'Город 3', 'Город 4']),
        ('date_up', ['Город 3', 'Город 1', 'Город 2', 'Город 4']),
        ('default_auth', ['Город 3', 'Город 1', 'Город 2', 'Город 4']),
        ('', ['Город 3', 'Город 1', 'Город 2', 'Город 4']),
        ('wrong value', ['Город 1', 'Город 2', 'Город 3', 'Город 4'])
    ]
)
def test__correct_order_of_sorted_cities_on_page__auth_user(setup_db__region_pk__sorting, client, sort_value, expected_value):
    """
    Проверяет корректность порядка отображения карточек с городами на странице для авторизованного пользователя.
    """
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?sort=' + sort_value)
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'city_card_1'}).find('div', {'class': 'h4'}).get_text(expected_value[0])
    assert source.find('div', {'id': 'city_card_2'}).find('div', {'class': 'h4'}).get_text(expected_value[1])
    assert source.find('div', {'id': 'city_card_3'}).find('div', {'class': 'h4'}).get_text(expected_value[2])
    assert source.find('div', {'id': 'city_card_4'}).find('div', {'class': 'h4'}).get_text(expected_value[3])


@pytest.mark.django_db
@pytest.mark.parametrize(
    'sort_value, expected_value', [
        ('name_down', ['Город 1', 'Город 2', 'Город 3', 'Город 4']),
        ('name_up', ['Город 1', 'Город 2', 'Город 3', 'Город 4']),
        ('date_down', ['Город 1', 'Город 2', 'Город 3', 'Город 4']),
        ('date_up', ['Город 1', 'Город 2', 'Город 3', 'Город 4']),
        ('default_guest', ['Город 1', 'Город 2', 'Город 3', 'Город 4']),
        ('', ['Город 1', 'Город 2', 'Город 3', 'Город 4']),
        ('wrong value', ['Город 1', 'Город 2', 'Город 3', 'Город 4'])
    ]
)
def test__correct_order_of_sorted_cities_on_page__guest(setup_db__region_pk__sorting, client, sort_value, expected_value):
    """
    Проверяет корректность порядка отображения карточек с городами на странице для неавторизованного пользователя.
    """
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?sort=' + sort_value)
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert expected_value[0] in source.find('div', {'id': 'city_card_1'}).find('div', {'class': 'h4'}).get_text()
    assert expected_value[1] in source.find('div', {'id': 'city_card_2'}).find('div', {'class': 'h4'}).get_text()
    assert expected_value[2] in source.find('div', {'id': 'city_card_3'}).find('div', {'class': 'h4'}).get_text()
    assert expected_value[3] in source.find('div', {'id': 'city_card_4'}).find('div', {'class': 'h4'}).get_text()


@pytest.mark.django_db
def test__page_has_no_sort_buttons_for_guest(setup_db__region_pk__sorting, client):
    """
    Проверяет отсутствие на странице кнопок для сортировки для неавторизованного пользователя.
    """
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'filter_and_sorting'}) is None
    assert source.find('div', {'id': 'sorting'}) is None
    assert source.find('div', {'id': 'sorting_by_name'}) is None


@pytest.mark.django_db
def test__page_has_sort_buttons_for_auth_user(setup_db__region_pk__sorting, client):
    """
    Проверяет существование на странице наличия кнопок для сортировки для авторизованного пользователя.
    """
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block = source.find('div', {'id': 'block-filter_and_sorting'})
    section = block.find('div', {'id': 'section-sorting'})
    subsection_by_name = section.find('div', {'id': 'subsection-sorting-by_name'})
    subsection_by_date_of_visit = section.find('div', {'id': 'subsection-sorting-by_date_of_visit'})
    sorting_by_name_down_link = subsection_by_name.find('a', {
        'href': reverse('region-selected', kwargs={'pk': 1}) + '?sort=name_down'
    })
    sorting_by_name_up_link = subsection_by_name.find('a', {
        'href': reverse('region-selected', kwargs={'pk': 1}) + '?sort=name_up'
    })
    sorting_by_date_down_link = subsection_by_date_of_visit.find('a', {
        'href': reverse('region-selected', kwargs={'pk': 1}) + '?sort=date_down'
    })
    sorting_by_date_up_link = subsection_by_date_of_visit.find('a', {
        'href': reverse('region-selected', kwargs={'pk': 1}) + '?sort=date_up'
    })

    assert block
    assert section
    assert subsection_by_name
    assert subsection_by_date_of_visit
    assert sorting_by_name_down_link
    assert sorting_by_name_up_link
    assert sorting_by_date_down_link
    assert sorting_by_date_up_link
