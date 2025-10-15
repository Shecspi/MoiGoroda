"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from region.models import Region


@pytest.mark.integration
@pytest.mark.django_db
class TestRegionListByCountryAPI:
    """Тесты для API endpoint region_list_by_country"""

    def test_returns_regions_for_valid_country(
        self, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест возврата регионов для валидной страны"""
        Region.objects.create(
            title='Region1',
            full_name='Region 1',
            country=test_country,
            type=test_region_type,
            iso3166='RU-R1',
        )

        client = APIClient()
        response = client.get(reverse('region-list-by-country'), {'country_id': test_country.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_returns_400_without_country_id(self) -> None:
        """Тест возврата 400 без обязательного параметра country_id"""
        client = APIClient()
        response = client.get(reverse('region-list-by-country'))

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'country_id' in response.data['detail']

    def test_returns_empty_list_for_country_without_regions(self) -> None:
        """Тест возврата пустого списка для страны без регионов"""
        from country.models import Country

        empty_country = Country.objects.create(name='Empty Country', code='EC')

        client = APIClient()
        response = client.get(reverse('region-list-by-country'), {'country_id': empty_country.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_returns_regions_sorted_by_title(
        self, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест что регионы отсортированы по названию"""
        Region.objects.create(
            title='Я',
            full_name='Я регион',
            country=test_country,
            type=test_region_type,
            iso3166='RU-YA',
        )
        Region.objects.create(
            title='А',
            full_name='А регион',
            country=test_country,
            type=test_region_type,
            iso3166='RU-A',
        )

        client = APIClient()
        response = client.get(reverse('region-list-by-country'), {'country_id': test_country.id})

        assert response.status_code == status.HTTP_200_OK
        titles = [region['title'] for region in response.data]
        assert titles[0] == 'А регион'


@pytest.mark.integration
@pytest.mark.django_db
class TestSearchRegionAPI:
    """Тесты для API endpoint search_region"""

    def test_searches_regions_by_query(
        self, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест поиска регионов по запросу"""
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

        client = APIClient()
        response = client.get(reverse('search-region'), {'query': 'Москов'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert 'Московская' in response.data[0]['title']

    def test_returns_400_without_query(self) -> None:
        """Тест возврата 400 без обязательного параметра query"""
        client = APIClient()
        response = client.get(reverse('search-region'))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_searches_case_insensitive(
        self, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест что поиск регистронезависимый"""
        Region.objects.create(
            title='Московская',
            full_name='Московская область',
            country=test_country,
            type=test_region_type,
            iso3166='RU-MOS',
        )

        client = APIClient()
        response = client.get(reverse('search-region'), {'query': 'московская'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_filters_by_country_code(
        self, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест фильтрации по коду страны"""
        from country.models import Country

        other_country = Country.objects.create(name='США', code='US')

        Region.objects.create(
            title='Московская',
            full_name='Московская область',
            country=test_country,
            type=test_region_type,
            iso3166='RU-MOS',
        )
        Region.objects.create(
            title='Moscow',
            full_name='Moscow State',
            country=other_country,
            type=test_region_type,
            iso3166='US-MOS',
        )

        client = APIClient()
        response = client.get(reverse('search-region'), {'query': 'Москов', 'country': 'RU'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert 'Московская' in response.data[0]['title']

    def test_returns_empty_list_when_no_matches(self) -> None:
        """Тест возврата пустого списка когда нет совпадений"""
        client = APIClient()
        response = client.get(reverse('search-region'), {'query': 'НесуществующийРегион'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_returns_full_name_in_results(
        self, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест что в результатах возвращается полное название"""
        Region.objects.create(
            title='Московская',
            full_name='Московская область',
            country=test_country,
            type=test_region_type,
            iso3166='RU-MOS',
        )

        client = APIClient()
        response = client.get(reverse('search-region'), {'query': 'Московская'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['title'] == 'Московская область'

    def test_returns_region_id_in_results(
        self, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест что в результатах возвращается ID региона"""
        region = Region.objects.create(
            title='Московская',
            full_name='Московская область',
            country=test_country,
            type=test_region_type,
            iso3166='RU-MOS',
        )

        client = APIClient()
        response = client.get(reverse('search-region'), {'query': 'Московская'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['id'] == region.id

