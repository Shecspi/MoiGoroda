"""
Тестирует работу сортировки городов конкретного региона.
Страница тестирования '/region/1'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


import pytest

from city.models import City, VisitedCity
from utils.CitiesByRegionMixin import CitiesByRegionMixin

from bs4 import BeautifulSoup
from django.urls import reverse
from django.db.models import OuterRef, Exists, Subquery, DateField


@pytest.mark.django_db
@pytest.mark.parametrize(
    'sort_value, expected_value', [
        ('name_down', ['Город 1', 'Город 2', 'Город 3', 'Город 4']),
        ('name_up', ['Город 4', 'Город 3', 'Город 2', 'Город 1']),
        ('date_down', ['Город 2', 'Город 1', 'Город 3', 'Город 4']),
        ('date_up', ['Город 3', 'Город 1', 'Город 2', 'Город 4']),
        ('default_auth', ['Город 3', 'Город 1', 'Город 2', 'Город 4']),
        ('default_guest', ['Город 1', 'Город 2', 'Город 3', 'Город 4'])
    ]
)
def test__CitiesByRegionMixin_apply_sort_to_queryset(setup_db_for_sorting, sort_value, expected_value):
    """
    Проверяет корректность работы метода сортировки Queryset - CitiesByRegionMixin.apply_sort_to_queryset().
    """
    mixin = CitiesByRegionMixin()
    queryset = City.objects.filtelr(region=1).annotate(
        is_visited=Exists(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db_for_sorting)
        ),
        date_of_visit=Subquery(
            VisitedCity.objects.filter(city__id=OuterRef('pk'), user=setup_db_for_sorting).values('date_of_visit'),
            output_field=DateField()
        )
    ).values_list('title')

    result = [city for city in mixin.apply_sort_to_queryset(queryset, sort_value).values_list('title', flat=True)]
    assert result == expected_value


@pytest.mark.django_db
def test__page_has_no_sort_buttons_for_guest(setup_db_for_sorting, client):
    """
    Проверяет отсутствие на странице кнопок для сортировки для неавторизованного пользователя.
    """
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert source.find('div', {'id': 'filter_and_sorting'}) is None
    assert source.find('div', {'id': 'sorting'}) is None
    assert source.find('div', {'id': 'sorting_by_name'}) is None


@pytest.mark.django_db
def test__page_has_sort_buttons_for_auth_user(setup_db_for_sorting, client):
    """
    Проверяет существование на странице наличия кнопок для сортировки для авторизованного пользователя.
    """
    client.login(username='username', password='password')
    response = client.get(reverse('region-selected', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    filter_and_sorting_block = source.find('div', {'id': 'filter_and_sorting'}).find('div', {'id': 'sorting'})
    sorting_by_name_block = filter_and_sorting_block.find('div', {'id': 'sorting_by_name'})
    sorting_by_date_of_visit_block = filter_and_sorting_block.find('div', {'id': 'sorting_by_date_of_visit'})
    sorting_by_name_down_link = sorting_by_name_block.find('a', {
        'href': reverse('region-selected', kwargs={'pk': 1}) + '?sort=name_down'
    })
    sorting_by_name_up_link = sorting_by_name_block.find('a', {
        'href': reverse('region-selected', kwargs={'pk': 1}) + '?sort=name_up'
    })
    sorting_by_date_down_link = sorting_by_date_of_visit_block.find('a', {
        'href': reverse('region-selected', kwargs={'pk': 1}) + '?sort=date_down'
    })
    sorting_by_date_up_link = sorting_by_date_of_visit_block.find('a', {
        'href': reverse('region-selected', kwargs={'pk': 1}) + '?sort=date_up'
    })

    assert filter_and_sorting_block
    assert sorting_by_name_block
    assert sorting_by_date_of_visit_block
    assert sorting_by_name_down_link
    assert sorting_by_name_up_link
    assert sorting_by_date_down_link
    assert sorting_by_date_up_link
