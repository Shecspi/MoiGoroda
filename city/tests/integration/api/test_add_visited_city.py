# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Регрессии совместимого DMR endpoint ``/api/city/visited/add``."""

import json
from datetime import date
from typing import Any, Type

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from rest_framework import status

from city.models import City, VisitedCity
from collection.models import Collection
from country.models import Country
from region.models import Region, RegionType


@pytest.fixture
def city() -> City:
    country = Country.objects.create(name='Россия', code='RU')
    region_type = RegionType.objects.create(title='область')
    region = Region.objects.create(
        title='Тверская область',
        country=country,
        type=region_type,
        iso3166='RU-TVE',
        full_name='Тверская область',
    )
    return City.objects.create(
        title='Тверь',
        region=region,
        country=country,
        coordinate_width=56.8587,
        coordinate_longitude=35.9176,
    )


def post_visit(client: Client, city: City, visit_date: str) -> Any:
    return client.post(
        reverse('api__add_visited_city'),
        data=json.dumps({'city': city.id, 'date_of_visit': visit_date, 'rating': 5}),
        content_type='application/json',
    )


@pytest.mark.integration
class TestAddVisitedCityAccess:
    """Проверяет доступ и разрешённые методы без обращения к базе."""

    url = reverse('api__add_visited_city')

    def test_guest_cannot_access(self, client: Client, mocker: Any) -> None:
        """Ломается, если DMR миграция открывает создание гостю."""
        context_reader = mocker.patch('city.api.visited.get_city_collection_context')

        response = client.post(self.url, {})

        assert response.status_code == status.HTTP_403_FORBIDDEN
        context_reader.assert_not_called()

    @pytest.mark.parametrize('method', ['get', 'put', 'patch', 'delete'])
    def test_prohibited_methods(self, client: Client, method: str) -> None:
        """Ломается, если create route начинает принимать лишний HTTP метод."""
        response = getattr(client, method)(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.integration
@pytest.mark.django_db
class TestAddVisitedCityValidation:
    """Проверяет msgspec validation до обращения к ORM."""

    url = reverse('api__add_visited_city')

    def test_rejects_invalid_typed_body(
        self, client: Client, django_user_model: Type[User]
    ) -> None:
        """Ломается, если DMR DTO принимает невалидную дату или рейтинг."""
        user = django_user_model.objects.create_user(username='testuser', password='password')
        client.force_login(user)

        response = client.post(
            self.url,
            {'city': 'not-a-number', 'date_of_visit': 'not-a-date', 'rating': 'invalid'},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_session_post_requires_csrf_token(self, django_user_model: Type[User]) -> None:
        """Ломается, если DMR create controller обходит CSRF session-auth защиты."""
        user = django_user_model.objects.create_user(username='csrf-user', password='password')
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)

        response = client.post(self.url, {'city': 1, 'date_of_visit': '2024-01-15', 'rating': 5})

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.django_db
class TestAddVisitedCityCollectionContext:
    def test_first_and_repeat_visits_return_additive_collection_context(
        self,
        client: Client,
        django_user_model: Type[User],
        city: City,
    ) -> None:
        user = django_user_model.objects.create_user(username='testuser', password='password')
        client.force_login(user)
        collection = Collection.objects.create(title='<Верхневолжье>')
        collection.city.add(city)

        first_response = post_visit(client, city, '2026-08-01')
        repeat_response = post_visit(client, city, '2026-08-02')

        expected_context = {
            'city': {'id': city.id, 'title': 'Тверь', 'url': f'/city/{city.id}'},
            'common_collections': {
                'count': 1,
                'single': {
                    'id': collection.id,
                    'title': '<Верхневолжье>',
                    'url': f'/collection/{collection.id}/list',
                },
                'catalog_url': f'/collection/?city={city.id}',
            },
        }
        for response, visit_date in (
            (first_response, date(2026, 8, 1)),
            (repeat_response, date(2026, 8, 2)),
        ):
            assert response.status_code == status.HTTP_200_OK
            payload = response.json()
            assert payload['status'] == 'success'
            assert payload['city']['city'] == city.id
            assert payload['city']['city_title'] == 'Тверь'
            visit = VisitedCity.objects.get(user=user, city=city, date_of_visit=visit_date)
            assert payload['visit'] == {
                'id': visit.id,
                'city': city.id,
                'city_title': 'Тверь',
                'region_title': 'Тверская область',
                'country': 'Россия',
                'date_of_visit': visit_date.isoformat(),
                'has_magnet': False,
                'impression': None,
                'impression_html': '',
                'rating': 5,
                'lat': '56.8587',
                'lon': '35.9176',
            }
            assert payload['collection_context'] == expected_context

    def test_multiple_common_collections_return_city_filtered_catalog_url(
        self,
        client: Client,
        django_user_model: Type[User],
        city: City,
    ) -> None:
        """Для toast двух коллекций API возвращает URL каталога выбранного города."""
        user = django_user_model.objects.create_user(username='catalog-user', password='password')
        client.force_login(user)
        for title in ('Верхняя Волга', 'Древние города'):
            collection = Collection.objects.create(title=title)
            collection.city.add(city)

        response = post_visit(client, city, '2026-08-01')

        collections = response.json()['collection_context']['common_collections']
        assert response.status_code == status.HTTP_200_OK
        assert collections == {
            'count': 2,
            'single': None,
            'catalog_url': f'/collection/?city={city.id}',
        }

    def test_context_error_returns_500_without_creating_visit(
        self,
        client: Client,
        django_user_model: Type[User],
        city: City,
        mocker: Any,
    ) -> None:
        user = django_user_model.objects.create_user(username='testuser', password='password')
        client.force_login(user)
        client.raise_request_exception = False
        mocker.patch(
            'city.api.visited.get_city_collection_context',
            side_effect=RuntimeError('collection read failed'),
        )

        response = post_visit(client, city, '2026-08-01')

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert not VisitedCity.objects.filter(user=user, city=city).exists()

    @pytest.mark.parametrize('case', ['invalid', 'unknown', 'duplicate'])
    def test_rejected_requests_do_not_read_collection_context(
        self,
        case: str,
        client: Client,
        django_user_model: Type[User],
        city: City,
        mocker: Any,
    ) -> None:
        user = django_user_model.objects.create_user(username='testuser', password='password')
        client.force_login(user)
        context_reader = mocker.patch('city.api.visited.get_city_collection_context')

        if case == 'invalid':
            response = post_visit(client, city, 'not-a-date')
        elif case == 'unknown':
            response = client.post(
                reverse('api__add_visited_city'),
                data=json.dumps({'city': city.id + 999, 'rating': 5}),
                content_type='application/json',
            )
        else:
            VisitedCity.objects.create(
                user=user,
                city=city,
                date_of_visit=date(2026, 8, 1),
                rating=5,
            )
            response = post_visit(client, city, '2026-08-01')

        assert response.status_code in {
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_409_CONFLICT,
        }
        context_reader.assert_not_called()
