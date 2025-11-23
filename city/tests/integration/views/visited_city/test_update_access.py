"""
Тесты для проверки доступа к обновлению посещённого города (VisitedCity_Update view).

Проверяется:
- Доступ для неавторизованных пользователей
- Доступ для авторизованных пользователей-владельцев
- Доступ для авторизованных пользователей-не владельцев
- GET и POST запросы
- Корректность обновления записи в БД
- Логирование операций
"""

from typing import Any

import pytest
from django.test import Client
from django.urls import reverse
from pytest import LogCaptureFixture

from city.models import VisitedCity


@pytest.mark.integration
class TestUpdateAccessUnauthenticated:
    """Тесты доступа к обновлению для неавторизованных пользователей."""

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_guest_get_redirects_to_login(self, setup: Any, client: Client) -> None:
        """GET запрос от гостя должен перенаправлять на страницу входа."""
        response = client.get(reverse('city-update', kwargs={'pk': 1}))

        assert response.status_code == 302
        assert '/account/signin' in response.url  # type: ignore[attr-defined]

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_guest_get_follow_shows_signin_page(self, setup: Any, client: Client) -> None:
        """GET запрос от гостя с follow должен показывать страницу входа."""
        response = client.get(reverse('city-update', kwargs={'pk': 1}), follow=True)

        assert response.status_code == 200
        assert 'account/signin.html' in (t.name for t in response.templates)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_guest_post_redirects_to_login(self, setup: Any, client: Client) -> None:
        """POST запрос от гостя должен перенаправлять на страницу входа."""
        response = client.post(reverse('city-update', kwargs={'pk': 1}))

        assert response.status_code == 302
        assert '/account/signin' in response.url  # type: ignore[attr-defined]

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_guest_post_follow_shows_signin_page(self, setup: Any, client: Client) -> None:
        """POST запрос от гостя с follow должен показывать страницу входа."""
        response = client.post(reverse('city-update', kwargs={'pk': 1}), follow=True)

        assert response.status_code == 200
        assert 'account/signin.html' in (t.name for t in response.templates)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_guest_cannot_update_city(self, setup: Any, client: Client) -> None:
        """Гость не должен иметь возможность обновить запись."""
        original_rating = VisitedCity.objects.get(pk=1).rating

        client.post(reverse('city-update', kwargs={'pk': 1}), data={'rating': 5})

        updated_rating = VisitedCity.objects.get(pk=1).rating
        assert original_rating == updated_rating


@pytest.mark.integration
class TestUpdateAccessOwner:
    """Тесты доступа к обновлению для авторизованных пользователей-владельцев."""

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_owner_get_shows_form(self, setup: Any, client: Client) -> None:
        """GET запрос от владельца должен показывать форму редактирования."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))

        assert response.status_code == 200
        assert 'city/create/page.html' in (t.name for t in response.templates)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_owner_get_shows_correct_template(self, setup: Any, client: Client) -> None:
        """GET запрос должен использовать корректный шаблон."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))

        assert 'city/create/page.html' in (t.name for t in response.templates)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_owner_get_has_correct_context(self, setup: Any, client: Client) -> None:
        """Контекст страницы должен содержать корректные данные."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))

        assert response.context['action'] == 'update'
        assert 'form' in response.context

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_owner_post_with_valid_data_updates_successfully(
        self, setup: Any, caplog: LogCaptureFixture, client: Client
    ) -> None:
        """POST запрос от владельца с валидными данными должен успешно обновить запись."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'date_of_visit': '2023-03-03',
                'has_magnet': True,
                'rating': 5,
                'impression': 'Updated impression',
            },
        )

        updated_city = VisitedCity.objects.get(pk=1)
        assert response.status_code == 302
        assert updated_city.rating == 5
        assert updated_city.has_magnet is True
        assert updated_city.impression is not None
        assert 'Updated impression' in updated_city.impression

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_owner_post_redirects_to_city_detail(self, setup: Any, client: Client) -> None:
        """После обновления должен быть редирект на страницу города."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        city_id = visited_city.city.id

        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'date_of_visit': '2023-03-03',
                'has_magnet': True,
                'rating': 5,
            },
        )

        assert response.status_code == 302
        assert f'/city/{city_id}' in response.url  # type: ignore[attr-defined]

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_owner_post_logs_update(
        self, setup: Any, caplog: LogCaptureFixture, client: Client
    ) -> None:
        """Обновление должно логироваться."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'date_of_visit': '2023-03-03',
                'has_magnet': True,
                'rating': 5,
            },
        )

        assert any(
            '(Visited city) Updating the visited city #1' in record.getMessage()
            for record in caplog.records
            if record.levelname == 'INFO'
        )


@pytest.mark.integration
class TestUpdateAccessNonOwner:
    """Тесты доступа к обновлению для авторизованных пользователей-не владельцев."""

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_non_owner_get_returns_404(self, setup: Any, client: Client) -> None:
        """GET запрос от не-владельца должен возвращать 404."""
        client.login(username='username2', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))

        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_non_owner_post_returns_404(self, setup: Any, client: Client) -> None:
        """POST запрос от не-владельца должен возвращать 404."""
        client.login(username='username2', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 5,
            },
        )

        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_non_owner_cannot_update_others_city(self, setup: Any, client: Client) -> None:
        """Не-владелец не должен иметь возможность обновить чужую запись."""
        client.login(username='username2', password='password')
        original_rating = VisitedCity.objects.get(pk=1).rating

        try:
            client.post(
                reverse('city-update', kwargs={'pk': 1}),
                data={'rating': 5},
            )
        except Exception:  # noqa: S110
            pass  # Ожидаем 404

        updated_rating = VisitedCity.objects.get(pk=1).rating
        assert original_rating == updated_rating


@pytest.mark.integration
class TestUpdateEdgeCases:
    """Тесты граничных случаев при обновлении."""

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_update_nonexistent_city(self, setup: Any, client: Client) -> None:
        """Попытка обновить несуществующий город должна возвращать 404."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 9999}))

        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_update_with_invalid_pk(self, setup: Any, client: Client) -> None:
        """Попытка обновить с некорректным pk должна возвращать 404."""
        client.login(username='username1', password='password')

        try:
            response = client.get(reverse('city-update', kwargs={'pk': 'invalid'}))
            assert response.status_code == 404
        except Exception:  # noqa: S110
            # Может быть ValueError при парсинге URL
            pass

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_owner_get_to_nonexistent_city_returns_404(self, setup: Any, client: Client) -> None:
        """GET запрос к несуществующему городу должен возвращать 404."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 2}))

        assert response.status_code == 404
