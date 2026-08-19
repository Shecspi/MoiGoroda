# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Контрактные тесты DMR API добавления и редактирования посещений городов."""

from datetime import date
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from rest_framework import status

from city.models import City, VisitedCity
from country.models import Country
from region.models import Region, RegionType


@pytest.fixture
def visit_api_data() -> dict[str, Any]:
    """Создаёт минимальные связанные данные для API посещений."""
    country = Country.objects.create(name='Россия', code='RU')
    region_type = RegionType.objects.create(title='Область')
    region = Region.objects.create(
        title='Московская',
        full_name='Московская область',
        country=country,
        type=region_type,
        iso3166='RU-MOS',
    )
    city = City.objects.create(
        title='Москва',
        country=country,
        region=region,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )
    owner = User.objects.create_user(username='owner', password='password')
    other_user = User.objects.create_user(username='other', password='password')
    return {'city': city, 'owner': owner, 'other_user': other_user}


@pytest.mark.integration
@pytest.mark.django_db
class TestVisitedCityController:
    """Проверяет consumer-visible контракт DMR контроллера посещений."""

    def test_post_keeps_existing_success_response_contract(
        self, client: Client, visit_api_data: dict[str, Any]
    ) -> None:
        """Ломается, если DMR миграция меняет body успешного создания."""
        VisitedCity.objects.create(
            user=visit_api_data['other_user'],
            city=visit_api_data['city'],
            rating=4,
        )
        client.force_login(visit_api_data['owner'])

        response = client.post(
            reverse('api__add_visited_city'),
            {
                'city': visit_api_data['city'].id,
                'date_of_visit': '2024-01-15',
                'rating': 5,
                'has_magnet': '1',
                'impression': 'Отличная поездка',
                'from': 'city-page',
            },
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert data['city']['city'] == visit_api_data['city'].id
        assert data['city']['id'] != visit_api_data['city'].id
        assert data['city']['city_title'] == 'Москва'
        assert data['city']['date_of_visit'] == '2024-01-15'
        assert data['city']['rating'] == 5
        assert data['city']['has_magnet'] is True
        assert data['city']['number_of_visits'] == 1

    def test_post_returns_conflict_for_duplicate_visit_date(
        self, client: Client, visit_api_data: dict[str, Any]
    ) -> None:
        """Ломается, если повторная дата визита создаёт дубликат вместо 409."""
        city = visit_api_data['city']
        owner = visit_api_data['owner']
        VisitedCity.objects.create(user=owner, city=city, date_of_visit=date(2024, 1, 15), rating=4)
        client.force_login(owner)

        response = client.post(
            reverse('api__add_visited_city'),
            {'city': city.id, 'date_of_visit': '2024-01-15', 'rating': 5},
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert 'уже сохранили посещение' in response.json()['message']

    def test_get_returns_only_owners_visit(
        self, client: Client, visit_api_data: dict[str, Any]
    ) -> None:
        """Ломается, если идентификатор чужого визита раскрывает его данные."""
        visit = VisitedCity.objects.create(
            user=visit_api_data['owner'],
            city=visit_api_data['city'],
            date_of_visit=date(2024, 1, 15),
            rating=4,
            has_magnet=True,
            impression='Старые впечатления',
        )
        client.force_login(visit_api_data['other_user'])

        response = client.get(reverse('api__visited_city_detail', kwargs={'visit_id': visit.id}))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_returns_not_found_for_another_users_visit(
        self, client: Client, visit_api_data: dict[str, Any]
    ) -> None:
        """Ломается, если чужое посещение можно изменить по известному ID."""
        visit = VisitedCity.objects.create(
            user=visit_api_data['owner'],
            city=visit_api_data['city'],
            rating=4,
        )
        client.force_login(visit_api_data['other_user'])

        response = client.patch(
            reverse('api__visited_city_detail', kwargs={'visit_id': visit.id}),
            {'rating': 5},
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        visit.refresh_from_db()
        assert visit.rating == 4

    def test_session_patch_requires_csrf_token(self, visit_api_data: dict[str, Any]) -> None:
        """Ломается, если DMR PATCH обходит CSRF защиту session auth."""
        visit = VisitedCity.objects.create(
            user=visit_api_data['owner'],
            city=visit_api_data['city'],
            rating=4,
        )
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(visit_api_data['owner'])

        response = csrf_client.patch(
            reverse('api__visited_city_detail', kwargs={'visit_id': visit.id}),
            {'rating': 5},
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_returns_editable_visit_and_city_summary(
        self, client: Client, visit_api_data: dict[str, Any]
    ) -> None:
        """Ломается, если edit-модалка не получает visit и city в одном ответе."""
        visit = VisitedCity.objects.create(
            user=visit_api_data['owner'],
            city=visit_api_data['city'],
            date_of_visit=date(2024, 1, 15),
            rating=4,
            has_magnet=True,
            impression='Старые впечатления',
        )
        client.force_login(visit_api_data['owner'])

        response = client.get(reverse('api__visited_city_detail', kwargs={'visit_id': visit.id}))

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['visit'] == {
            'id': visit.id,
            'city': visit_api_data['city'].id,
            'city_title': 'Москва',
            'region_title': 'Московская область',
            'country': 'Россия',
            'date_of_visit': '2024-01-15',
            'rating': 4,
            'has_magnet': True,
            'impression': 'Старые впечатления',
            'impression_html': '<p>Старые впечатления</p>',
            'lat': '55.7558',
            'lon': '37.6173',
        }
        assert data['city']['id'] == visit_api_data['city'].id
        assert data['city']['title'] == 'Москва'
        assert data['city']['country'] == 'Россия'

    def test_get_sanitizes_rendered_impression_html(
        self, client: Client, visit_api_data: dict[str, Any]
    ) -> None:
        """Ломается, если API отдаёт HTML впечатления без markdownify sanitization."""
        visit = VisitedCity.objects.create(
            user=visit_api_data['owner'],
            city=visit_api_data['city'],
            date_of_visit=date(2024, 1, 15),
            rating=4,
            impression='Привет <script>alert(1)</script>',
        )
        client.force_login(visit_api_data['owner'])

        response = client.get(reverse('api__visited_city_detail', kwargs={'visit_id': visit.id}))

        assert response.status_code == status.HTTP_200_OK
        assert '<script>' not in response.json()['visit']['impression_html']

    def test_patch_updates_visit_without_allowing_city_change(
        self, client: Client, visit_api_data: dict[str, Any]
    ) -> None:
        """Ломается, если PATCH меняет город или не сохраняет разрешённые поля."""
        city = visit_api_data['city']
        second_city = City.objects.create(
            title='Тверь',
            country=city.country,
            region=city.region,
            coordinate_width=56.8587,
            coordinate_longitude=35.9176,
        )
        visit = VisitedCity.objects.create(
            user=visit_api_data['owner'],
            city=city,
            date_of_visit=date(2024, 1, 15),
            rating=4,
        )
        client.force_login(visit_api_data['owner'])

        response = client.patch(
            reverse('api__visited_city_detail', kwargs={'visit_id': visit.id}),
            {
                'city': second_city.id,
                'date_of_visit': '2024-02-15',
                'rating': 5,
                'has_magnet': True,
                'impression': 'Обновлённые впечатления',
            },
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        visit.refresh_from_db()
        assert visit.city_id == city.id
        assert visit.date_of_visit == date(2024, 1, 15)

    def test_patch_updates_all_editable_fields(
        self, client: Client, visit_api_data: dict[str, Any]
    ) -> None:
        """Ломается, если PATCH игнорирует одно из полей формы редактирования."""
        visit = VisitedCity.objects.create(
            user=visit_api_data['owner'],
            city=visit_api_data['city'],
            date_of_visit=date(2024, 1, 15),
            rating=4,
        )
        client.force_login(visit_api_data['owner'])

        response = client.patch(
            reverse('api__visited_city_detail', kwargs={'visit_id': visit.id}),
            {
                'date_of_visit': '2024-02-15',
                'rating': 5,
                'has_magnet': True,
                'impression': 'Обновлённые впечатления',
            },
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_200_OK
        visit.refresh_from_db()
        assert visit.date_of_visit == date(2024, 2, 15)
        assert visit.rating == 5
        assert visit.has_magnet is True
        assert visit.impression == 'Обновлённые впечатления'
        assert response.json()['visit']['id'] == visit.id

    def test_patch_rejects_duplicate_date_for_same_city(
        self, client: Client, visit_api_data: dict[str, Any]
    ) -> None:
        """Ломается, если PATCH нарушает уникальность пары город-дата визита."""
        city = visit_api_data['city']
        owner = visit_api_data['owner']
        visit = VisitedCity.objects.create(
            user=owner, city=city, date_of_visit=date(2024, 1, 15), rating=4
        )
        VisitedCity.objects.create(user=owner, city=city, date_of_visit=date(2024, 2, 15), rating=5)
        client.force_login(owner)

        response = client.patch(
            reverse('api__visited_city_detail', kwargs={'visit_id': visit.id}),
            {'date_of_visit': '2024-02-15', 'rating': 3, 'has_magnet': False},
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        visit.refresh_from_db()
        assert visit.date_of_visit == date(2024, 1, 15)

    @pytest.mark.parametrize(
        'payload',
        [
            {'rating': 6},
            {'date_of_visit': 'not-a-date'},
        ],
    )
    def test_patch_rejects_invalid_typed_fields(
        self, client: Client, visit_api_data: dict[str, Any], payload: dict[str, Any]
    ) -> None:
        """Ломается, если PATCH принимает рейтинг или дату вне серверных правил."""
        visit = VisitedCity.objects.create(
            user=visit_api_data['owner'],
            city=visit_api_data['city'],
            rating=4,
        )
        client.force_login(visit_api_data['owner'])

        response = client.patch(
            reverse('api__visited_city_detail', kwargs={'visit_id': visit.id}),
            payload,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
