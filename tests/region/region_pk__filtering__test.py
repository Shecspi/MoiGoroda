"""
Тестирует работу abkmnhfwbb городов конкретного региона.
Страница тестирования '/region/<id>'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from datetime import datetime

from django.db.models import Exists, OuterRef, DateField, Subquery, BooleanField

from city.models import City, VisitedCity
from region.models import Area, Region
from utils.CitiesByRegionMixin import CitiesByRegionMixin
from utils.VisitedCityMixin import VisitedCityMixin

from bs4 import BeautifulSoup
from django.urls import reverse


@pytest.fixture
def setup_db__filtering__reion_pk(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Округ 1')
    region = Region.objects.create(id=1, area=area, title='Регион 1', type='область', iso3166='RU-RU')
    cities = (
        ('Город 1', f'{datetime.now().year}-01-01', True),
        ('Город 2', f'{datetime.now().year}-01-01', True),
        ('Город 3', f'{datetime.now().year - 1}-01-01', True),
        ('Город 4', f'{datetime.now().year - 2}-01-01', False),
        ('Город 5', f'{datetime.now().year - 2}-01-01', False),
        ('Город 6', f'{datetime.now().year - 2}-01-01', False)
    )
    for c in cities:
        city = City.objects.create(title=c[0], region=region, coordinate_width=1, coordinate_longitude=1)
        VisitedCity.objects.create(
            user=user, region=region, city=city, date_of_visit=c[1], has_magnet=c[2], rating=3
        )

    return user


@pytest.mark.django_db
@pytest.mark.parametrize(
    'filter_value, expected_value', [
        ('magnet', ['Город 4', 'Город 5', 'Город 6']),
        ('current_year', ['Город 1', 'Город 2']),
        ('last_year', ['Город 3'])
    ]
)
def test__filtering__correct_value(setup_db__filtering__reion_pk, filter_value, expected_value):
    mixin = CitiesByRegionMixin()
    queryset = City.objects.filter(region=1).annotate(
        is_visited=Exists(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db__filtering__reion_pk)
        ),
        date_of_visit=Subquery(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db__filtering__reion_pk).values(
                'date_of_visit'),
            output_field=DateField()
        ),
        has_magnet=Subquery(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db__filtering__reion_pk).values(
                'has_magnet'),
            output_field=BooleanField()
        )
    ).values_list('title')

    result = [city for city in mixin.apply_filter_to_queryset(queryset, filter_value).values_list('title', flat=True)]
    assert result == expected_value


def test__filtering__incorrect_value(setup_db__filtering__reion_pk):
    mixin = VisitedCityMixin()
    queryset = City.objects.filter(region=1).annotate(
        is_visited=Exists(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db__filtering__reion_pk)
        ),
        date_of_visit=Subquery(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db__filtering__reion_pk).values(
                'date_of_visit'),
            output_field=DateField()
        ),
        has_magnet=Subquery(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db__filtering__reion_pk).values(
                'has_magnet'),
            output_field=BooleanField()
        )
    ).values_list('title')

    with pytest.raises(KeyError) as info:
        mixin.apply_filter_to_queryset(queryset, 'wrong value').values_list('city__title', flat=True)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'filter_value, expected_value', (
            ('magnet', ['Город 4', 'Город 5', 'Город 6']),
            ('current_year', ['Город 1', 'Город 2']),
            ('last_year', ['Город 3']),
            ('wrong_value', ['Город 1', 'Город 2', 'Город 3', 'Город 4', 'Город 5', 'Город 6'])
    )
)
def test__correct_order_of_filtered_cities_on_page__auth_user(setup_db__filtering__reion_pk,
                                                              client, filter_value, expected_value):
    """
    Тестируется порядок отображения карточек при фильтрации.
    Содержимое карточек более подробно тестируется в другом файле.
    """
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?filter=' + filter_value)
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    for number in range(1, len(expected_value) + 1):
        card_city = source.find('div', {'id': f'city_card_{number}'})
        header_of_cadr_city = card_city.find('div', {'class': 'h4'})
        assert expected_value[number - 1] in header_of_cadr_city.get_text()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'filter_value, expected_value', (
            ('magnet', ['Город 1', 'Город 2', 'Город 3', 'Город 4', 'Город 5', 'Город 6']),
            ('current_year', ['Город 1', 'Город 2', 'Город 3', 'Город 4', 'Город 5', 'Город 6']),
            ('last_year', ['Город 1', 'Город 2', 'Город 3', 'Город 4', 'Город 5', 'Город 6'])
    )
)
def test__correct_order_of_filtered_cities_on_page__guest(setup_db__filtering__reion_pk,
                                                          client, filter_value, expected_value):
    """
    Тестируется порядок отображения карточек при фильтрации.
    Содержимое карточек более подробно тестируется в другом файле.

    Для неавторизованного пользователя фильтрация недоступна,
    поэтому при любом значении 'filter' результат будет одинаковый.
    """
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + '?filter=' + filter_value)
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    for number in range(1, len(expected_value) + 1):
        card_city = source.find('div', {'id': f'city_card_{number}'})
        header_of_cadr_city = card_city.find('div', {'class': 'h4'})
        assert expected_value[number - 1] in header_of_cadr_city.get_text()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'sort_value', [
        'name_down', 'name_up', 'date_down', 'date_up', ''
    ]
)
def test__filter_buttons__auth_user(setup_db__filtering__reion_pk, client, sort_value):
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}) + (f'?sort={sort_value}' if sort_value else ''))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block_filter_and_sorting = source.find('div', {'id': 'block-filter_and_sorting'})
    block_filtering = source.find('div', {'id': 'block-filtering'})
    print(reverse('region-selected', kwargs={'pk': 1}) + (f'?filter=magnet&sort={sort_value}' if sort_value else '?filter=magnet'))
    print(block_filtering.find_all('a'))
    button_filtering_by_magnet = block_filtering.find('a', {
        'href': reverse('region-selected', kwargs={'pk': 1}) + (f'?filter=magnet&sort={sort_value}' if sort_value else '?filter=magnet&sort=default_auth')
    })
    button_filtering_by_current_year = source.find('a', {
        'href': reverse('region-selected', kwargs={'pk': 1}) + (f'?filter=current_year&sort={sort_value}' if sort_value else '?filter=current_year&sort=default_auth')
    })
    button_filtering_by_last_year = source.find('a', {
        'href': reverse('region-selected', kwargs={'pk': 1}) + (f'?filter=last_year&sort={sort_value}' if sort_value else '?filter=last_year&sort=default_auth')
    })

    assert block_filter_and_sorting
    assert block_filtering
    assert button_filtering_by_magnet
    assert button_filtering_by_current_year
    assert button_filtering_by_last_year


@pytest.mark.django_db
def test__filter_buttons__guest(setup_db__filtering__reion_pk, client):
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'block-filter_and_sorting'}) is None
