"""
Тестирует работу сортировки городов конкретного региона.
Страница тестирования '/city/all'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


import pytest
from datetime import datetime

from city.models import City, VisitedCity
from region.models import Area, Region
from utils.VisitedCityMixin import VisitedCityMixin

from bs4 import BeautifulSoup
from django.urls import reverse
from django.db.models import OuterRef, Exists, Subquery, DateField


@pytest.fixture
def setup_db(client, django_user_model):
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
        ('magnet', ['Город 6', 'Город 5', 'Город 4']),
        ('current_year', ['Город 2', 'Город 1']),
        ('last_year', ['Город 3'])
    ]
)
def test__method_apply_filter_to_queryset_correct_value(setup_db, filter_value, expected_value):
    """
    Проверяет корректность работы метода фильтрации Queryset - VisitedCityMixin.apply_filter_to_queryset().
    Должны отображаться только города, попадающие под условие 'filter_value'.
    """
    mixin = VisitedCityMixin()
    queryset = VisitedCity.objects.filter(user=setup_db)

    result = [city for city in mixin.apply_filter_to_queryset(queryset, filter_value).values_list('city__title', flat=True)]
    assert result == expected_value


def test__method_filter_sort_to_queryset_incorrect_value(setup_db):
    """
    Проверяет корректность работы метода фильтрации Queryset - VisitedCityMixin.apply_filter_to_queryset().
    При некорректных данных он должен вернуть исключение KeyError.
    """
    mixin = VisitedCityMixin()
    queryset = VisitedCity.objects.filter(user=setup_db)

    with pytest.raises(KeyError) as info:
        mixin.apply_filter_to_queryset(queryset, 'wrong value').values_list('city__title', flat=True)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'sort_value, expected_value', (
        ('magnet', ['Город 6', 'Город 5', 'Город 4']),
        ('current_year', ['Город 2', 'Город 1']),
        ('last_year', ['Город 3'])
    )
)
def test__correct_order_of_sorted_cities_on_page(setup_db, client, sort_value, expected_value):
    """
    Проверяет корректность порядка отображения карточек с городами на странице для авторизованного пользователя.
    Неавторизованный пользователь не имеет доступа на эту страницу.
    """
    client.login(username='username', password='password')
    response = client.get(reverse('city-all') + '?sort=' + sort_value)
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    for number in range(1, len(expected_value) + 1):
        assert source.find(
            'div', {'id': f'city_card_{number}'}
        ).find(
            'div', {'class': 'h4'}
        ).get_text(expected_value[number - 1])


@pytest.mark.django_db
def test__page_has_filter_buttons_for_auth_user(setup_db, client):
    """
    Проверяет существование на странице наличия кнопок для фильтрации для авторизованного пользователя.
    """
    mixin = VisitedCityMixin()
    client.login(username='username', password='password')
    response = client.get(reverse('city-all'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    block_filter_and_sorting = source.find('div', {'id': 'block-filter_and_sorting'})
    block_filtering = source.find('div', {'id': 'block-filtering'})
    button_filtering_by_magnet = block_filtering.find('a', {
        'href': reverse('city-all') + '?' + mixin.get_url_params('magnet', '')
    })
    button_filtering_by_current_year = source.find('a', {
        'href': reverse('city-all') + '?' + mixin.get_url_params('current_year', '')
    })
    button_filtering_by_last_year = source.find('a', {
        'href': reverse('city-all') + '?' + mixin.get_url_params('last_year', '')
    })

    assert block_filter_and_sorting
    assert block_filtering
    assert button_filtering_by_magnet
    assert button_filtering_by_current_year
    assert button_filtering_by_last_year
