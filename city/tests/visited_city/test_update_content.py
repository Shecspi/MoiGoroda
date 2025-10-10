"""
Тесты для проверки валидации формы обновления посещённого города.

Проверяется:
- Валидация данных формы
- Граничные значения
- Обработка ошибок валидации
- Предзаполнение формы существующими данными
"""

from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from city.models import VisitedCity


class TestUpdateFormValidation:
    """Тесты валидации формы обновления."""

    @pytest.mark.django_db
    def test_update_with_valid_data(self, setup: Any, client: Client) -> None:
        """Обновление с валидными данными должно быть успешным."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'date_of_visit': '2023-05-15',
                'has_magnet': True,
                'rating': 4,
                'impression': 'Great city!'
            }
        )
        
        assert response.status_code == 302
        updated = VisitedCity.objects.get(pk=1)
        assert updated.rating == 4
        assert updated.has_magnet is True

    @pytest.mark.django_db
    def test_update_with_missing_required_city(self, setup: Any, client: Client) -> None:
        """Обновление без указания города должно возвращать ошибку."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 4,
            }
        )
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    @pytest.mark.django_db
    def test_update_with_missing_required_rating(self, setup: Any, client: Client) -> None:
        """Обновление без указания рейтинга должно возвращать ошибку."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
            }
        )
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    @pytest.mark.django_db
    def test_update_rating_boundary_values(self, setup: Any, client: Client) -> None:
        """Тестирование граничных значений рейтинга."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        # Минимальное значение
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 1,
            }
        )
        assert response.status_code == 302
        assert VisitedCity.objects.get(pk=1).rating == 1
        
        # Максимальное значение
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 5,
            }
        )
        assert response.status_code == 302
        assert VisitedCity.objects.get(pk=1).rating == 5

    @pytest.mark.django_db
    def test_update_with_optional_date_of_visit(self, setup: Any, client: Client) -> None:
        """Обновление без даты посещения должно быть успешным (поле опциональное)."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 4,
                'date_of_visit': '',
            }
        )
        
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_update_with_optional_impression(self, setup: Any, client: Client) -> None:
        """Обновление без впечатлений должно быть успешным (поле опциональное)."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 4,
                'impression': '',
            }
        )
        
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_update_has_magnet_unchecked(self, setup: Any, client: Client) -> None:
        """Тест обновления с неотмеченным чекбоксом has_magnet."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 4,
                # has_magnet не передаем - должно быть False
            }
        )
        
        assert response.status_code == 302
        assert VisitedCity.objects.get(pk=1).has_magnet is False


class TestUpdateFormPrefill:
    """Тесты предзаполнения формы существующими данными."""

    @pytest.mark.django_db
    def test_form_prefilled_with_existing_data(self, setup: Any, client: Client) -> None:
        """Форма должна быть предзаполнена существующими данными."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        
        visited_city = VisitedCity.objects.get(pk=1)
        form = response.context['form']
        
        assert form.initial['city'] == visited_city.city.id
        assert form.initial['country'] == visited_city.city.country.id

    @pytest.mark.django_db
    def test_form_shows_current_rating(self, setup: Any, client: Client) -> None:
        """Форма должна показывать текущий рейтинг."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        
        assert response.context['form'].instance.rating == visited_city.rating

    @pytest.mark.django_db
    def test_form_shows_current_has_magnet(self, setup: Any, client: Client) -> None:
        """Форма должна показывать текущее значение has_magnet."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        
        assert response.context['form'].instance.has_magnet == visited_city.has_magnet
