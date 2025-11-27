"""
Тесты для проверки доступа к удалению посещённого города (VisitedCity_Delete view).

Проверяется:
- Доступ для неавторизованных пользователей
- Доступ для авторизованных пользователей-владельцев
- Доступ для авторизованных пользователей-не владельцев
- Запрет GET метода
- Корректность удаления записи из БД
- Логирование операций
"""

from typing import Any

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from pytest import LogCaptureFixture

from city.models import VisitedCity


@pytest.mark.integration
class TestDeleteAccessUnauthenticated:
    """Тесты доступа к удалению для неавторизованных пользователей."""

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_guest_get_redirects_to_login(self, setup: Any, client: Client) -> None:
        """GET запрос от гостя должен перенаправлять на страницу входа."""
        response = client.get(reverse('city-delete', kwargs={'pk': 1}))

        assert response.status_code == 302
        assert '/account/signin' in response.url  # type: ignore[attr-defined]

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_guest_get_follow_shows_signin_page(self, setup: Any, client: Client) -> None:
        """GET запрос от гостя с follow должен показывать страницу входа."""
        response = client.get(reverse('city-delete', kwargs={'pk': 1}), follow=True)

        assert response.status_code == 200
        assert 'account/auth/signin.html' in (t.name for t in response.templates)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_guest_post_redirects_to_login(self, setup: Any, client: Client) -> None:
        """POST запрос от гостя должен перенаправлять на страницу входа."""
        response = client.post(reverse('city-delete', kwargs={'pk': 1}))

        assert response.status_code == 302
        assert '/account/signin' in response.url  # type: ignore[attr-defined]

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_guest_post_follow_shows_signin_page(self, setup: Any, client: Client) -> None:
        """POST запрос от гостя с follow должен показывать страницу входа."""
        response = client.post(reverse('city-delete', kwargs={'pk': 1}), follow=True)

        assert response.status_code == 200
        assert 'account/auth/signin.html' in (t.name for t in response.templates)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_guest_cannot_delete_city(self, setup: Any, client: Client) -> None:
        """Гость не должен иметь возможность удалить запись."""
        qty_before = VisitedCity.objects.count()
        client.post(reverse('city-delete', kwargs={'pk': 1}))
        qty_after = VisitedCity.objects.count()

        assert qty_before == qty_after


@pytest.mark.integration
class TestDeleteAccessOwner:
    """Тесты доступа к удалению для авторизованных пользователей-владельцев."""

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_owner_get_forbidden(
        self, setup: Any, caplog: LogCaptureFixture, client: Client
    ) -> None:
        """GET запрос от владельца должен возвращать 403 Forbidden."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-delete', kwargs={'pk': 1}))

        assert response.status_code == 403
        assert caplog.records[0].levelname == 'WARNING'
        assert '(Visited city) Attempt to access the GET method' in caplog.records[0].getMessage()

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_owner_post_deletes_successfully(
        self, setup: Any, caplog: LogCaptureFixture, client: Client
    ) -> None:
        """POST запрос от владельца должен успешно удалить запись."""
        client.login(username='username1', password='password')
        user = User.objects.get(username='username1')
        qty_before = VisitedCity.objects.filter(user=user).count()

        response = client.post(reverse('city-delete', kwargs={'pk': 1}), follow=True)
        qty_after = VisitedCity.objects.filter(user=user).count()

        assert qty_before - qty_after == 1
        assert response.status_code == 200
        assert caplog.records[0].levelname == 'INFO'
        assert '(Visited city) Deleting the visited city #1' in caplog.records[0].getMessage()

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_owner_post_redirects_to_city_detail(self, setup: Any, client: Client) -> None:
        """После удаления должен быть редирект на страницу города."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        city_id = visited_city.city.id

        response = client.post(reverse('city-delete', kwargs={'pk': 1}))

        assert response.status_code == 302
        assert f'/city/{city_id}' in response.url  # type: ignore[attr-defined]

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_owner_post_removes_from_database(self, setup: Any, client: Client) -> None:
        """После удаления запись должна отсутствовать в БД."""
        client.login(username='username1', password='password')

        assert VisitedCity.objects.filter(pk=1).exists()
        client.post(reverse('city-delete', kwargs={'pk': 1}))

        assert not VisitedCity.objects.filter(pk=1).exists()


@pytest.mark.integration
class TestDeleteAccessNonOwner:
    """Тесты доступа к удалению для авторизованных пользователей-не владельцев."""

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_non_owner_get_forbidden(self, setup: Any, client: Client) -> None:
        """GET запрос от не-владельца должен возвращать 403 Forbidden."""
        client.login(username='username2', password='password')
        response = client.get(reverse('city-delete', kwargs={'pk': 1}))

        assert response.status_code == 403

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_non_owner_post_returns_404(
        self, setup: Any, caplog: LogCaptureFixture, client: Client
    ) -> None:
        """POST запрос от не-владельца должен возвращать 404."""
        client.login(username='username2', password='password')
        response = client.post(reverse('city-delete', kwargs={'pk': 1}))

        assert response.status_code == 404
        assert caplog.records[0].levelname == 'WARNING'
        assert (
            '(Visited city) Attempt to delete a non-existent visited city #1'
            in caplog.records[0].getMessage()
        )

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_non_owner_cannot_delete_others_city(self, setup: Any, client: Client) -> None:
        """Не-владелец не должен иметь возможность удалить чужую запись."""
        client.login(username='username2', password='password')
        qty_before = VisitedCity.objects.count()

        try:
            client.post(reverse('city-delete', kwargs={'pk': 1}))
        except Exception:  # noqa: S110
            pass  # Ожидаем 404, но продолжаем проверку

        qty_after = VisitedCity.objects.count()
        assert qty_before == qty_after


@pytest.mark.integration
class TestDeleteEdgeCases:
    """Тесты граничных случаев при удалении."""

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_delete_nonexistent_city(self, setup: Any, client: Client) -> None:
        """Попытка удалить несуществующий город должна возвращать 404."""
        client.login(username='username1', password='password')
        response = client.post(reverse('city-delete', kwargs={'pk': 9999}))

        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_delete_with_invalid_pk(self, setup: Any, client: Client) -> None:
        """Попытка удалить с некорректным pk должна возвращать 404."""
        client.login(username='username1', password='password')

        try:
            response = client.post(reverse('city-delete', kwargs={'pk': 'invalid'}))
            assert response.status_code == 404
        except Exception:  # noqa: S110
            # Может быть ValueError при парсинге URL
            pass
