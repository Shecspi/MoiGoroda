"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime
from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from region.models import Region


@pytest.mark.e2e
@pytest.mark.django_db
def test_complete_region_browsing_workflow(
    client: Client,
    test_user: Any,
    test_country: Any,
    test_region_type: Any,
    test_area: Any,
) -> None:
    """E2E тест полного цикла просмотра регионов"""
    # Создаём регионы
    region1 = Region.objects.create(
        title='Московская',
        full_name='Московская область',
        country=test_country,
        type=test_region_type,
        area=test_area,
        iso3166='RU-MOS',
    )
    region2 = Region.objects.create(
        title='Ленинградская',
        full_name='Ленинградская область',
        country=test_country,
        type=test_region_type,
        area=test_area,
        iso3166='RU-LEN',
    )

    # Создаём города
    city1 = City.objects.create(
        title='Москва',
        region=region1,
        country=test_country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )
    _ = City.objects.create(
        title='Санкт-Петербург',
        region=region2,
        country=test_country,
        coordinate_width=59.9343,
        coordinate_longitude=30.3351,
    )

    # Авторизуемся
    client.force_login(test_user)

    # Шаг 1: Просматриваем список регионов
    response = client.get(reverse('region-all-list') + f'?country={test_country.code}')
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert 'Московская область' in content
    assert 'Ленинградская область' in content

    # Шаг 2: Просматриваем карту регионов
    response = client.get(reverse('region-all-map') + f'?country={test_country.code}')
    assert response.status_code == 200
    assert 'all_regions' in response.context

    # Шаг 3: Переходим к списку городов региона
    response = client.get(reverse('region-selected-list', kwargs={'pk': region1.pk}))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert 'Москва' in content

    # Шаг 4: Помечаем город как посещённый
    VisitedCity.objects.create(user=test_user, city=city1, rating=5)

    # Шаг 5: Проверяем что статистика обновилась
    response = client.get(reverse('region-all-list') + f'?country={test_country.code}')
    assert response.status_code == 200
    assert response.context['qty_of_visited_regions'] >= 1


@pytest.mark.e2e
@pytest.mark.django_db
def test_region_filtering_workflow(
    client: Client,
    test_user: Any,
    test_country: Any,
    test_region: Region,
) -> None:
    """E2E тест работы с фильтрами в регионе"""
    # Создаём города
    city1 = City.objects.create(
        title='City1',
        region=test_region,
        country=test_country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )
    city2 = City.objects.create(
        title='City2',
        region=test_region,
        country=test_country,
        coordinate_width=56.0,
        coordinate_longitude=38.0,
    )

    # Посещаем города
    VisitedCity.objects.create(
        user=test_user,
        city=city1,
        has_magnet=True,
        date_of_visit=datetime.now().date(),
        rating=5,
    )
    VisitedCity.objects.create(user=test_user, city=city2, has_magnet=False, rating=5)

    client.force_login(test_user)

    # Шаг 1: Просматриваем все города
    response = client.get(reverse('region-selected-list', kwargs={'pk': test_region.pk}))
    assert response.status_code == 200

    # Шаг 2: Фильтруем только города с сувениром
    response = client.get(
        reverse('region-selected-list', kwargs={'pk': test_region.pk}) + '?filter=magnet'
    )
    assert response.status_code == 200
    assert response.context['filter'] == 'magnet'

    # Шаг 3: Фильтруем города текущего года
    response = client.get(
        reverse('region-selected-list', kwargs={'pk': test_region.pk}) + '?filter=current_year'
    )
    assert response.status_code == 200
    assert response.context['filter'] == 'current_year'


@pytest.mark.e2e
@pytest.mark.django_db
def test_region_sorting_workflow(
    client: Client,
    test_user: Any,
    test_country: Any,
    test_region: Region,
) -> None:
    """E2E тест работы с сортировкой в регионе"""
    # Создаём города с разными датами
    city1 = City.objects.create(
        title='А-город',
        region=test_region,
        country=test_country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )
    city2 = City.objects.create(
        title='Я-город',
        region=test_region,
        country=test_country,
        coordinate_width=56.0,
        coordinate_longitude=38.0,
    )

    VisitedCity.objects.create(
        user=test_user, city=city1, date_of_visit=datetime(2024, 1, 1).date(), rating=5
    )
    VisitedCity.objects.create(
        user=test_user, city=city2, date_of_visit=datetime(2024, 12, 31).date(), rating=5
    )

    client.force_login(test_user)

    # Шаг 1: Сортировка по названию
    response = client.get(
        reverse('region-selected-list', kwargs={'pk': test_region.pk}) + '?sort=name_up'
    )
    assert response.status_code == 200
    assert response.context['sort'] == 'name_up'

    # Шаг 2: Сортировка по дате последнего посещения
    response = client.get(
        reverse('region-selected-list', kwargs={'pk': test_region.pk})
        + '?sort=last_visit_date_down'
    )
    assert response.status_code == 200
    assert response.context['sort'] == 'last_visit_date_down'


@pytest.mark.e2e
@pytest.mark.django_db
def test_region_map_and_list_switching(
    client: Client, test_user: Any, test_region: Region, test_city: City
) -> None:
    """E2E тест переключения между картой и списком"""
    client.force_login(test_user)

    # Шаг 1: Просматриваем список городов
    response = client.get(reverse('region-selected-list', kwargs={'pk': test_region.pk}))
    assert response.status_code == 200
    assert 'region/region_selected__list.html' in [t.name for t in response.templates]

    # Шаг 2: Переключаемся на карту
    response = client.get(reverse('region-selected-map', kwargs={'pk': test_region.pk}))
    assert response.status_code == 200
    assert 'region/region_selected__map.html' in [t.name for t in response.templates]

    # Шаг 3: Проверяем что контекст содержит нужные данные
    assert 'all_cities' in response.context
    assert 'region_name' in response.context


@pytest.mark.e2e
@pytest.mark.django_db
def test_region_search_workflow(
    client: Client, test_country: Any, test_region_type: Any, test_area: Any
) -> None:
    """E2E тест поиска регионов"""
    # Создаём несколько регионов
    Region.objects.create(
        title='Московская',
        full_name='Московская область',
        country=test_country,
        type=test_region_type,
        area=test_area,
        iso3166='RU-MOS',
    )
    Region.objects.create(
        title='Ленинградская',
        full_name='Ленинградская область',
        country=test_country,
        type=test_region_type,
        area=test_area,
        iso3166='RU-LEN',
    )
    Region.objects.create(
        title='Мурманская',
        full_name='Мурманская область',
        country=test_country,
        type=test_region_type,
        area=test_area,
        iso3166='RU-MUR',
    )

    # Шаг 1: Ищем через API по букве М
    response = client.get(reverse('search-region'), {'query': 'М'})
    assert response.status_code == 200
    assert len(response.json()) >= 2  # Московская и Мурманская

    # Шаг 2: Уточняем поиск
    response = client.get(reverse('search-region'), {'query': 'Моск'})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert 'Московская' in response.json()[0]['title']


@pytest.mark.e2e
@pytest.mark.django_db
def test_unauthenticated_user_region_workflow(
    client: Client, test_country: Any, test_region: Region, test_city: City
) -> None:
    """E2E тест работы с регионами для неавторизованного пользователя"""
    # Шаг 1: Просматриваем список регионов
    response = client.get(reverse('region-all-list') + f'?country={test_country.code}')
    assert response.status_code == 200
    # Не должно быть информации о посещениях
    assert 'qty_of_visited_regions' in response.context
    assert response.context['qty_of_visited_regions'] == 0

    # Шаг 2: Просматриваем список городов региона
    response = client.get(reverse('region-selected-list', kwargs={'pk': test_region.pk}))
    assert response.status_code == 200
    # Не должно быть информации о посещениях
    assert 'number_of_visited_cities' in response.context
    assert response.context['number_of_visited_cities'] == 0
