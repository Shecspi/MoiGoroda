# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Интеграционные тесты DMR-фрагментов региональных списков."""

from datetime import date
from typing import Any

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from region.models import Region


@pytest.mark.django_db
@pytest.mark.integration
class TestRegionListFragments:
    def test_selected_region_fragment_preserves_filter_sort_and_page(
        self,
        client: Client,
        test_user: Any,
        test_country: Any,
        test_region: Region,
    ) -> None:
        """Фрагмент города региона содержит актуальные зависимые от посещений блоки."""
        for number in range(17):
            city = City.objects.create(
                title=f'Город {number:02d}',
                country=test_country,
                region=test_region,
                coordinate_width=55.0 + number,
                coordinate_longitude=37.0 + number,
            )
            VisitedCity.objects.create(
                user=test_user,
                city=city,
                rating=5,
                date_of_visit=date(2024, 1, 1),
            )
        client.force_login(test_user)

        response = client.get(
            reverse('region-selected-list-fragment', kwargs={'pk': test_region.pk})
            + '?filter=visited&sort=name_down&page=2'
        )

        content = response.content.decode()
        document = BeautifulSoup(content, 'html.parser')
        container = document.select_one('[data-visited-city-refresh]')
        assert response.status_code == 200
        assert container is not None
        assert content.count('data-visited-city-refresh') == 1
        assert container.select_one('#toolbar') is not None
        results = container.select_one('#region-selected-list-results')
        assert results is not None
        assert 'Город 00' in results.get_text()
        assert 'Город 16' not in results.get_text()
        assert 'Посещено 17 городов из 17' in container.get_text(' ', strip=True)
        assert container.select_one('[aria-label="Пагинация"]') is not None
        assert container.select_one('#region-timeline-modal') is not None
        assert container.select_one('#offcanvasRight') is not None
        assert response.context['filter'] == 'visited'
        assert response.context['sort'] == 'name_down'
        assert response.context['page_obj'].number == 2
        assert '<html' not in content

    def test_all_regions_fragment_preserves_country_filter_and_page(
        self,
        client: Client,
        test_user: Any,
        test_country: Any,
        test_region_type: Any,
        test_city: City,
    ) -> None:
        """Фрагмент страны возвращает её региональный прогресс и текущую страницу."""
        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)
        for number in range(17):
            Region.objects.create(
                title=f'Фрагментский {number:02d}',
                full_name=f'Фрагментский регион {number:02d}',
                country=test_country,
                type=test_region_type,
                iso3166=f'RU-F{number:02d}',
            )
        client.force_login(test_user)

        response = client.get(
            reverse('region-all-list-fragment'),
            data={'country': test_country.code, 'filter': 'Фрагментский', 'page': 2},
        )

        content = response.content.decode()
        document = BeautifulSoup(content, 'html.parser')
        container = document.select_one('[data-visited-city-refresh]')
        assert response.status_code == 200
        assert container is not None
        assert content.count('data-visited-city-refresh') == 1
        assert container.select_one('#toolbar') is not None
        results = container.select_one('#region-all-list-results')
        assert results is not None
        assert 'Фрагментский регион' in results.get_text()
        assert 'Посещено 1 регион из 18' in container.get_text(' ', strip=True)
        assert container.select_one('[aria-label="Пагинация"]') is not None
        assert response.context['country_code'] == test_country.code
        assert response.context['page_obj'].number == 2
        assert '<html' not in content

    @pytest.mark.parametrize(
        ('url_name', 'kwargs', 'query'),
        [
            ('region-selected-list-fragment', {'pk': 1}, ''),
            ('region-all-list-fragment', {}, '?country=RU'),
        ],
    )
    def test_guest_gets_forbidden_response(
        self, client: Client, url_name: str, kwargs: dict[str, int], query: str
    ) -> None:
        """DMR-фрагменты не перенаправляют гостя на страницу входа."""
        response = client.get(reverse(url_name, kwargs=kwargs) + query)

        assert response.status_code == 403
