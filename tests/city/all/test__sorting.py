"""
Тестирует работу сортировки городов конкретного региона.
Страница тестирования '/city/all'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


import pytest

from city.models import City, VisitedCity
from region.models import Area, Region
from utils.VisitedCityMixin import VisitedCityMixin

from bs4 import BeautifulSoup
from django.urls import reverse
from django.db.models import OuterRef, Exists, Subquery, DateField


@pytest.fixture
def setup_db_for_sorting(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(id=1, area=area, title='Регион 1', type='область', iso3166='RU-RU')
    city_1 = City.objects.create(title='Город 1', region=region, coordinate_width=1, coordinate_longitude=1)
    city_2 = City.objects.create(title='Город 2', region=region, coordinate_width=1, coordinate_longitude=1)
    city_3 = City.objects.create(title='Город 3', region=region, coordinate_width=1, coordinate_longitude=1)
    city_4 = City.objects.create(title='Город 4', region=region, coordinate_width=1, coordinate_longitude=1)
    visited_city_1 = VisitedCity.objects.create(
        user=user, region=region, city=city_1, date_of_visit="2022-01-01", has_magnet=False, rating=3
    )
    visited_city_2 = VisitedCity.objects.create(
        user=user, region=region, city=city_2, has_magnet=False, rating=3
    )
    visited_city_3 = VisitedCity.objects.create(
        user=user, region=region, city=city_3, date_of_visit="2023-01-01", has_magnet=False, rating=3
    )

    return user


@pytest.mark.django_db
@pytest.mark.parametrize(
    'sort_value, expected_value', [
        ('name_down', ['Город 1', 'Город 2', 'Город 3']),
        ('name_up', ['Город 3', 'Город 2', 'Город 1']),
        ('date_down', ['Город 2', 'Город 1', 'Город 3']),
        ('date_up', ['Город 3', 'Город 1', 'Город 2']),
        ('default', ['Город 3', 'Город 1', 'Город 2']),
    ]
)
def test__method_apply_sort_to_queryset_correct_value(setup_db_for_sorting, sort_value, expected_value):
    """
    Проверяет корректность работы метода сортировки Queryset - VisitedCityMixin.apply_sort_to_queryset().
    Должны отображаться только посещённые города.
    """
    mixin = VisitedCityMixin()
    queryset = VisitedCity.objects.filter(user=setup_db_for_sorting)

    result = [city for city in mixin.apply_sort_to_queryset(queryset, sort_value).values_list('city__title', flat=True)]
    assert result == expected_value


def test__method_apply_sort_to_queryset_incorrect_value(setup_db_for_sorting):
    """
    Проверяет корректность работы метода сортировки Queryset - CitiesByRegionMixin.apply_sort_to_queryset().
    При некорректных данных он должен вернуть исключение KeyError.
    """
    mixin = VisitedCityMixin()
    queryset = VisitedCity.objects.filter(user=setup_db_for_sorting)

    with pytest.raises(KeyError) as info:
        mixin.apply_sort_to_queryset(queryset, 'wrong value').values_list('title', flat=True)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'sort_value, expected_value', [
        ('name_down', ['Город 1', 'Город 2', 'Город 3']),
        ('name_up', ['Город 3', 'Город 2', 'Город 1']),
        ('date_down', ['Город 2', 'Город 1', 'Город 3']),
        ('date_up', ['Город 3', 'Город 1', 'Город 2']),
        ('default', ['Город 3', 'Город 1', 'Город 2']),
        ('', ['Город 3', 'Город 1', 'Город 2']),
        ('wrong value', ['Город 1', 'Город 2', 'Город 3'])
    ]
)
def test__correct_order_of_sorted_cities_on_page(setup_db_for_sorting, client, sort_value, expected_value):
    """
    Проверяет корректность порядка отображения карточек с городами на странице для авторизованного пользователя.
    Неавторизованный пользователь не имеет доступа на эту страницу.
    """
    client.login(username='username', password='password')
    response = client.get(reverse('city-all') + '?sort=' + sort_value)
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'city_card_1'}).find('div', {'class': 'h4'}).get_text(expected_value[0])
    assert source.find('div', {'id': 'city_card_2'}).find('div', {'class': 'h4'}).get_text(expected_value[1])
    assert source.find('div', {'id': 'city_card_3'}).find('div', {'class': 'h4'}).get_text(expected_value[2])


@pytest.mark.django_db
def test__page_has_sort_buttons_for_auth_user(setup_db_for_sorting, client):
    """
    Проверяет существование на странице наличия кнопок для сортировки для авторизованного пользователя.
    Неавторизованный пользователь не имеет доступа на эту страницу.
    """
    client.login(username='username', password='password')
    response = client.get(reverse('city-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    filter_and_sorting_block = source.find('div', {'id': 'block-filter_and_sorting'}).find('div', {'id': 'sorting'})
    sorting_by_name_block = filter_and_sorting_block.find('div', {'id': 'sorting_by_name'})
    sorting_by_date_of_visit_block = filter_and_sorting_block.find('div', {'id': 'sorting_by_date_of_visit'})
    sorting_by_name_down_link = sorting_by_name_block.find('a', {
        'href': reverse('city-all') + '?sort=name_down'
    })
    sorting_by_name_up_link = sorting_by_name_block.find('a', {
        'href': reverse('city-all') + '?sort=name_up'
    })
    sorting_by_date_down_link = sorting_by_date_of_visit_block.find('a', {
        'href': reverse('city-all') + '?sort=date_down'
    })
    sorting_by_date_up_link = sorting_by_date_of_visit_block.find('a', {
        'href': reverse('city-all') + '?sort=date_up'
    })

    assert filter_and_sorting_block
    assert sorting_by_name_block
    assert sorting_by_date_of_visit_block
    assert sorting_by_name_down_link
    assert sorting_by_name_up_link
    assert sorting_by_date_down_link
    assert sorting_by_date_up_link
