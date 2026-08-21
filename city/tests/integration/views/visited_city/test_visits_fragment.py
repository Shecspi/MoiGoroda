# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Интеграционные тесты fragment пользовательских посещений города."""

from datetime import date
from typing import Any

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from country.models import Country


@pytest.mark.django_db
@pytest.mark.integration
class TestVisitedCityVisitsFragment:
    def test_authenticated_user_gets_only_own_complete_visits_surface(
        self, client: Client, django_user_model: Any
    ) -> None:
        user = django_user_model.objects.create_user(username='fragment-owner', password='pass123')
        other_user = django_user_model.objects.create_user(username='fragment-other', password='pass123')
        country = Country.objects.create(name='Россия', code='RU')
        city = City.objects.create(
            title='Тверь', country=country, coordinate_width=56.8, coordinate_longitude=36.0
        )
        VisitedCity.objects.create(
            user=user, city=city, date_of_visit=date(2026, 8, 5), rating=5
        )
        VisitedCity.objects.create(
            user=user, city=city, date_of_visit=date(2025, 8, 5), rating=4
        )
        VisitedCity.objects.create(
            user=other_user, city=city, date_of_visit=date(2024, 8, 5), rating=3
        )
        client.force_login(user)

        response = client.get(reverse('city-selected-visits-fragment', kwargs={'pk': city.pk}))

        document = BeautifulSoup(response.content, 'html.parser')
        root = document.select_one('#user-visits')
        assert response.status_code == 200
        assert root is not None
        assert root['data-city-id'] == str(city.pk)
        assert root.select_one('#user-visits-count').get_text(strip=True) == '2'
        assert len(root.select('[data-visit-id]')) == 2
        assert root.select_one('[data-action="edit-visited-city"]') is not None
        assert root.select_one('.delete_city') is not None
        assert '<html' not in response.content.decode()

    def test_guest_gets_forbidden_response(self, client: Client, django_user_model: Any) -> None:
        user = django_user_model.objects.create_user(username='fragment-owner', password='pass123')
        country = Country.objects.create(name='Россия', code='RU')
        city = City.objects.create(
            title='Тверь', country=country, coordinate_width=56.8, coordinate_longitude=36.0
        )
        VisitedCity.objects.create(user=user, city=city, rating=5)

        response = client.get(reverse('city-selected-visits-fragment', kwargs={'pk': city.pk}))

        assert response.status_code == 403
