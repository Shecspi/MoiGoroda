"""
Интеграционные тесты для функционала обновления и удаления посещённых городов.

Проверяются сценарии взаимодействия между update и delete операциями,
а также проверка корректности работы с различными наборами данных.
"""

from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from city.models import VisitedCity


class TestUpdateDeleteIntegration:
    """Интеграционные тесты для операций обновления и удаления."""

    @pytest.mark.django_db
    def test_update_then_delete_sequence(self, setup: Any, client: Client) -> None:
        """Последовательность обновления и затем удаления должна работать корректно."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        # Обновляем запись
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 5,
                'has_magnet': True,
            },
        )
        assert response.status_code == 302

        updated = VisitedCity.objects.get(pk=1)
        assert updated.rating == 5
        assert updated.has_magnet is True

        # Удаляем запись
        response = client.post(reverse('city-delete', kwargs={'pk': 1}))
        assert response.status_code == 302
        assert not VisitedCity.objects.filter(pk=1).exists()

    @pytest.mark.django_db
    def test_multiple_updates_preserve_data(self, setup: Any, client: Client) -> None:
        """Множественные обновления должны корректно сохранять данные."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        # Первое обновление
        client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 4,
                'impression': 'First update',
            },
        )

        # Второе обновление
        client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 5,
                'impression': 'Second update',
            },
        )

        final = VisitedCity.objects.get(pk=1)
        assert final.rating == 5
        assert final.impression == 'Second update'

    @pytest.mark.django_db
    def test_update_preserves_unchanged_fields(self, setup: Any, client: Client) -> None:
        """Обновление одного поля не должно затрагивать другие поля."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        original_date = visited_city.date_of_visit
        original_impression = visited_city.impression

        client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 5,
                'date_of_visit': original_date,
                'impression': original_impression,
            },
        )

        updated = VisitedCity.objects.get(pk=1)
        assert updated.date_of_visit == original_date
        assert updated.impression == original_impression
        assert updated.rating == 5


class TestMultipleUsersInteraction:
    """Тесты взаимодействия нескольких пользователей."""

    @pytest.mark.django_db
    def test_user_cannot_access_another_users_city(
        self, setup_multiple_cities: Any, client: Client
    ) -> None:
        """Пользователь не должен иметь доступ к городам другого пользователя."""
        client.login(username='username1', password='password')

        # Попытка получить доступ к городу пользователя 2
        response = client.get(reverse('city-update', kwargs={'pk': 3}))
        assert response.status_code == 404

        # Попытка обновить город пользователя 2
        response = client.post(reverse('city-update', kwargs={'pk': 3}), data={'rating': 1})
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_user_can_only_delete_own_cities(
        self, setup_multiple_cities: Any, client: Client
    ) -> None:
        """Пользователь может удалять только свои города."""
        client.login(username='username1', password='password')

        # Попытка удалить город пользователя 2
        response = client.post(reverse('city-delete', kwargs={'pk': 3}))
        assert response.status_code == 404
        assert VisitedCity.objects.filter(pk=3).exists()

        # Удаление собственного города
        response = client.post(reverse('city-delete', kwargs={'pk': 1}))
        assert response.status_code == 302
        assert not VisitedCity.objects.filter(pk=1).exists()

    @pytest.mark.django_db
    def test_user1_operations_dont_affect_user2(
        self, setup_multiple_cities: Any, client: Client
    ) -> None:
        """Операции пользователя 1 не должны влиять на данные пользователя 2."""
        user1_count_before = VisitedCity.objects.filter(user__username='username1').count()
        user2_count_before = VisitedCity.objects.filter(user__username='username2').count()

        client.login(username='username1', password='password')

        # Пользователь 1 удаляет свой город
        client.post(reverse('city-delete', kwargs={'pk': 1}))

        user1_count_after = VisitedCity.objects.filter(user__username='username1').count()
        user2_count_after = VisitedCity.objects.filter(user__username='username2').count()

        assert user1_count_before - user1_count_after == 1
        assert user2_count_before == user2_count_after


class TestComplexDataScenarios:
    """Тесты сложных сценариев работы с данными."""

    @pytest.mark.django_db
    def test_update_all_fields_at_once(self, setup: Any, client: Client) -> None:
        """Обновление всех полей одновременно должно работать корректно."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'date_of_visit': '2023-12-31',
                'has_magnet': True,
                'rating': 5,
                'impression': 'Complete update of all fields',
            },
        )

        assert response.status_code == 302
        updated = VisitedCity.objects.get(pk=1)
        assert str(updated.date_of_visit) == '2023-12-31'
        assert updated.has_magnet is True
        assert updated.rating == 5
        assert updated.impression == 'Complete update of all fields'

    @pytest.mark.django_db
    def test_update_rating_from_min_to_max(self, setup: Any, client: Client) -> None:
        """Изменение рейтинга от минимума к максимуму."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        for rating in range(1, 6):
            response = client.post(
                reverse('city-update', kwargs={'pk': 1}),
                data={
                    'city': visited_city.city.id,
                    'country': visited_city.city.country.id,
                    'region': visited_city.city.region.id if visited_city.city.region else '',
                    'rating': rating,
                },
            )
            assert response.status_code == 302
            assert VisitedCity.objects.get(pk=1).rating == rating

    @pytest.mark.django_db
    def test_update_toggle_has_magnet_multiple_times(self, setup: Any, client: Client) -> None:
        """Многократное переключение флага has_magnet."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        for has_magnet in [True, False, True, False]:
            data = {
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 3,
            }
            if has_magnet:
                data['has_magnet'] = True

            response = client.post(reverse('city-update', kwargs={'pk': 1}), data=data)
            assert response.status_code == 302
            assert VisitedCity.objects.get(pk=1).has_magnet == has_magnet

    @pytest.mark.django_db
    def test_update_with_very_long_impression(self, setup: Any, client: Client) -> None:
        """Обновление с очень длинным текстом впечатлений."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        long_impression = 'A' * 5000  # Очень длинный текст

        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 4,
                'impression': long_impression,
            },
        )

        assert response.status_code == 302
        updated = VisitedCity.objects.get(pk=1)
        assert updated.impression == long_impression

    @pytest.mark.django_db
    def test_update_with_special_characters_in_impression(self, setup: Any, client: Client) -> None:
        """Обновление с специальными символами в впечатлениях."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        special_impression = 'Test with <html> & "quotes" and \'apostrophes\' and 日本語'

        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 4,
                'impression': special_impression,
            },
        )

        assert response.status_code == 302
        updated = VisitedCity.objects.get(pk=1)
        assert updated.impression == special_impression


class TestEdgeCasesAndErrorHandling:
    """Тесты граничных случаев и обработки ошибок."""

    @pytest.mark.django_db
    def test_delete_already_deleted_city(self, setup: Any, client: Client) -> None:
        """Попытка удалить уже удалённый город должна возвращать 404."""
        client.login(username='username1', password='password')

        # Удаляем город
        client.post(reverse('city-delete', kwargs={'pk': 1}))

        # Пытаемся удалить еще раз
        response = client.post(reverse('city-delete', kwargs={'pk': 1}))
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_update_after_logout(self, setup: Any, client: Client) -> None:
        """Попытка обновить после выхода должна перенаправлять на логин."""
        client.login(username='username1', password='password')
        client.logout()

        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        assert response.status_code == 302
        assert '/account/signin' in response.url  # type: ignore[attr-defined]

    @pytest.mark.django_db
    def test_concurrent_update_attempts(self, setup: Any, client: Client) -> None:
        """Последовательные попытки обновления должны сохранять последнее значение."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        # Две быстрые последовательные попытки обновления
        client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 4,
            },
        )

        client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 5,
            },
        )

        # Должно быть сохранено последнее значение
        updated = VisitedCity.objects.get(pk=1)
        assert updated.rating == 5
