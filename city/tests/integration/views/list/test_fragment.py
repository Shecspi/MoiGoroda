# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Интеграционные тесты HTML-фрагмента списка посещённых городов."""

from datetime import date
from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from country.models import Country


@pytest.mark.django_db
@pytest.mark.integration
class TestVisitedCityListFragment:
    def test_authenticated_user_gets_query_aware_updated_blocks(
        self, client: Client, django_user_model: Any
    ) -> None:
        """Фрагмент содержит результаты и статистику без полной страницы."""
        user = django_user_model.objects.create_user(username='fragment-user', password='pass123')
        country = Country.objects.create(name='Россия', code='RU')
        matching_cities = [
            City.objects.create(
                title=f'Город {number:02d}',
                country=country,
                coordinate_width=55.0 + number,
                coordinate_longitude=37.0 + number,
            )
            for number in range(25)
        ]
        old_city = City.objects.create(
            title='Старый город',
            country=country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )
        for matching_city in matching_cities:
            VisitedCity.objects.create(
                user=user, city=matching_city, date_of_visit=date.today(), rating=5
            )
        VisitedCity.objects.create(user=user, city=old_city, date_of_visit=date(2020, 1, 1), rating=4)
        client.force_login(user)

        response = client.get(
            reverse('city-all-list-fragment')
            + '?country=RU&filter=current_year&sort=name_down&page=2'
        )

        content = response.content.decode()
        assert response.status_code == 200
        assert 'Город 00' in content
        assert 'Город 24' not in content
        assert 'Старый город' not in content
        assert 'city-list-results' in content
        assert 'toolbar-stats' in content
        assert 'городов' in content
        assert '<html' not in content
        assert 'id="toolbar"' not in content

    def test_guest_is_redirected_to_login(self, client: Client) -> None:
        """Фрагмент недоступен неаутентифицированному пользователю."""
        response = client.get(reverse('city-all-list-fragment'))

        assert response.status_code == 302
        assert response.url.startswith('/account/signin')  # type: ignore[attr-defined]

    def test_empty_selected_country_results_render_morphology_filters(
        self, client: Client, django_user_model: Any
    ) -> None:
        """Пустая выбранная страна рендерит самостоятельный include со склонением."""
        user = django_user_model.objects.create_user(
            username='empty-fragment-user', password='pass123'
        )
        russia = Country.objects.create(name='Россия', code='RU')
        kazakhstan = Country.objects.create(name='Казахстан', code='KZ')
        visited_city = City.objects.create(
            title='Алматы',
            country=kazakhstan,
            coordinate_width=43.2,
            coordinate_longitude=76.9,
        )
        VisitedCity.objects.create(
            user=user, city=visited_city, date_of_visit=date.today(), rating=5
        )
        client.force_login(user)

        response = client.get(reverse('city-all-list-fragment') + f'?country={russia.code}')

        assert response.status_code == 200
        assert 'Вы не посетили ни одного города в России.' in response.content.decode()
