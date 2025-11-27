"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""
# mypy: disable-error-code="attr-defined"

from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from region.models import Region


@pytest.mark.integration
@pytest.mark.django_db
class TestRegionListView:
    """Тесты для представления списка регионов"""

    def test_redirects_to_ru_without_country_param(self, client: Client) -> None:
        """Тест редиректа на RU если не указана страна"""
        response = client.get(reverse('region-all-list'))
        assert response.status_code == 302
        assert '?country=RU' in response.url

    def test_displays_regions_for_valid_country(
        self, client: Client, test_country: Any, test_region: Region
    ) -> None:
        """Тест отображения регионов для валидной страны"""
        response = client.get(reverse('region-all-list') + f'?country={test_country.code}')
        assert response.status_code == 200
        assert test_region.full_name.encode() in response.content

    def test_returns_404_for_invalid_country(self, client: Client) -> None:
        """Тест возврата 404 для невалидной страны"""
        response = client.get(reverse('region-all-list') + '?country=INVALID')
        assert response.status_code == 404

    def test_context_contains_country_info(
        self, client: Client, test_country: Any, test_region: Region
    ) -> None:
        """Тест что контекст содержит информацию о стране"""
        response = client.get(reverse('region-all-list') + f'?country={test_country.code}')
        assert response.status_code == 200
        assert 'country_code' in response.context
        assert response.context['country_code'] == test_country.code

    def test_filters_regions_by_search(
        self, client: Client, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест фильтрации регионов по поиску"""
        Region.objects.create(
            title='Московская',
            full_name='Московская область',
            country=test_country,
            type=test_region_type,
            iso3166='RU-MOS',
        )
        Region.objects.create(
            title='Ленинградская',
            full_name='Ленинградская область',
            country=test_country,
            type=test_region_type,
            iso3166='RU-LEN',
        )

        response = client.get(
            reverse('region-all-list') + f'?country={test_country.code}&filter=Московская'
        )
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert 'Московская' in content

    def test_authenticated_user_sees_visited_count(
        self,
        client: Client,
        test_user: Any,
        test_country: Any,
        test_region: Region,
        test_city: City,
    ) -> None:
        """Тест что авторизованный пользователь видит количество посещённых"""
        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        client.force_login(test_user)
        response = client.get(reverse('region-all-list') + f'?country={test_country.code}')

        assert response.status_code == 200
        assert 'qty_of_visited_regions' in response.context
        assert response.context['qty_of_visited_regions'] >= 0


@pytest.mark.integration
@pytest.mark.django_db
class TestRegionMapView:
    """Тесты для представления карты регионов"""

    def test_redirects_to_ru_without_country_param(self, client: Client) -> None:
        """Тест редиректа на RU если не указана страна"""
        response = client.get(reverse('region-all-map'))
        assert response.status_code == 302
        assert '?country=RU' in response.url

    def test_uses_correct_template(
        self, client: Client, test_country: Any, test_region: Region
    ) -> None:
        """Тест что используется правильный шаблон"""
        response = client.get(reverse('region-all-map') + f'?country={test_country.code}')
        assert response.status_code == 200
        assert 'region/all/map/page.html' in [t.name for t in response.templates]

    def test_context_contains_all_regions(
        self, client: Client, test_country: Any, test_region: Region
    ) -> None:
        """Тест что контекст содержит все регионы (для карты)"""
        response = client.get(reverse('region-all-map') + f'?country={test_country.code}')
        assert response.status_code == 200
        assert 'all_regions' in response.context


@pytest.mark.integration
@pytest.mark.django_db
class TestCitiesByRegionListView:
    """Тесты для представления списка городов региона"""

    def test_displays_cities_for_valid_region(
        self, client: Client, test_region: Region, test_city: City
    ) -> None:
        """Тест отображения городов для валидного региона"""
        response = client.get(reverse('region-selected-list', kwargs={'pk': test_region.pk}))
        assert response.status_code == 200
        assert test_city.title.encode() in response.content

    def test_returns_404_for_invalid_region(self, client: Client) -> None:
        """Тест возврата 404 для невалидного региона"""
        response = client.get(reverse('region-selected-list', kwargs={'pk': 999999}))
        assert response.status_code == 404

    def test_context_contains_region_info(
        self, client: Client, test_region: Region, test_city: City
    ) -> None:
        """Тест что контекст содержит информацию о регионе"""
        response = client.get(reverse('region-selected-list', kwargs={'pk': test_region.pk}))
        assert response.status_code == 200
        assert 'region_name' in response.context
        assert response.context['region_name'] == test_region.full_name

    def test_applies_sort_parameter(
        self,
        client: Client,
        test_user: Any,
        test_country: Any,
        test_region: Region,
    ) -> None:
        """Тест применения параметра сортировки"""
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

        VisitedCity.objects.create(user=test_user, city=city1, rating=5)
        VisitedCity.objects.create(user=test_user, city=city2, rating=5)

        client.force_login(test_user)
        response = client.get(
            reverse('region-selected-list', kwargs={'pk': test_region.pk}) + '?sort=name_down'
        )

        assert response.status_code == 200
        assert 'sort' in response.context
        assert response.context['sort'] == 'name_down'

    def test_applies_filter_parameter(
        self,
        client: Client,
        test_user: Any,
        test_country: Any,
        test_region: Region,
    ) -> None:
        """Тест применения параметра фильтра"""
        city1 = City.objects.create(
            title='City1',
            region=test_region,
            country=test_country,
            coordinate_width=55.0,
            coordinate_longitude=37.0,
        )

        VisitedCity.objects.create(user=test_user, city=city1, has_magnet=True, rating=5)

        client.force_login(test_user)
        response = client.get(
            reverse('region-selected-list', kwargs={'pk': test_region.pk}) + '?filter=magnet'
        )

        assert response.status_code == 200
        assert 'filter' in response.context
        assert response.context['filter'] == 'magnet'

    def test_authenticated_user_sees_visit_info(
        self,
        client: Client,
        test_user: Any,
        test_region: Region,
        test_city: City,
    ) -> None:
        """Тест что авторизованный пользователь видит информацию о посещениях"""
        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        client.force_login(test_user)
        response = client.get(reverse('region-selected-list', kwargs={'pk': test_region.pk}))

        assert response.status_code == 200
        assert 'number_of_visited_cities' in response.context
        assert response.context['number_of_visited_cities'] >= 1


@pytest.mark.integration
@pytest.mark.django_db
class TestCitiesByRegionMapView:
    """Тесты для представления карты городов региона"""

    def test_uses_correct_template(
        self, client: Client, test_region: Region, test_city: City
    ) -> None:
        """Тест что используется правильный шаблон"""
        response = client.get(reverse('region-selected-map', kwargs={'pk': test_region.pk}))
        assert response.status_code == 200
        assert 'region/selected/map/page.html' in [t.name for t in response.templates]

    def test_context_contains_all_cities(
        self, client: Client, test_region: Region, test_city: City
    ) -> None:
        """Тест что контекст содержит все города (для карты)"""
        response = client.get(reverse('region-selected-map', kwargs={'pk': test_region.pk}))
        assert response.status_code == 200
        assert 'all_cities' in response.context


@pytest.mark.integration
@pytest.mark.django_db
class TestEmbeddedMapView:
    """Тесты для встроенной карты региона"""

    def test_renders_embedded_map(self, client: Client) -> None:
        """Тест рендеринга встроенной карты"""
        response = client.get(
            reverse('region-embedded-map', kwargs={'quality': 'low', 'iso3166': 'RU-MOS'})
        )
        assert response.status_code == 200

    def test_sets_csp_header(self, client: Client) -> None:
        """Тест что устанавливается Content-Security-Policy заголовок"""
        response = client.get(
            reverse('region-embedded-map', kwargs={'quality': 'low', 'iso3166': 'RU-MOS'})
        )
        assert 'Content-Security-Policy' in response

    def test_accepts_different_quality_levels(self, client: Client) -> None:
        """Тест что принимаются разные уровни качества"""
        for quality in ['low', 'medium', 'high']:
            response = client.get(
                reverse('region-embedded-map', kwargs={'quality': quality, 'iso3166': 'RU-MOS'})
            )
            assert response.status_code == 200
