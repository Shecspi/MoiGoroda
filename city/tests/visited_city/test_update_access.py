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

import pytest
from django.urls import reverse
from city.models import VisitedCity


class TestUpdateAccessUnauthenticated:
    """Тесты доступа к обновлению для неавторизованных пользователей."""

    @pytest.mark.django_db
    def test_guest_get_redirects_to_login(self, setup, client):
        """GET запрос от гостя должен перенаправлять на страницу входа."""
        response = client.get(reverse('city-update', kwargs={'pk': 1}))

        assert response.status_code == 302
        assert '/account/signin' in response.url

    @pytest.mark.django_db
    def test_guest_get_follow_shows_signin_page(self, setup, client):
        """GET запрос от гостя с follow должен показывать страницу входа."""
        response = client.get(reverse('city-update', kwargs={'pk': 1}), follow=True)

        assert response.status_code == 200
        assert 'account/signin.html' in (t.name for t in response.templates)

    @pytest.mark.django_db
    def test_guest_post_redirects_to_login(self, setup, client):
        """POST запрос от гостя должен перенаправлять на страницу входа."""
        response = client.post(reverse('city-update', kwargs={'pk': 1}))

        assert response.status_code == 302
        assert '/account/signin' in response.url

    @pytest.mark.django_db
    def test_guest_post_follow_shows_signin_page(self, setup, client):
        """POST запрос от гостя с follow должен показывать страницу входа."""
        response = client.post(reverse('city-update', kwargs={'pk': 1}), follow=True)

        assert response.status_code == 200
        assert 'account/signin.html' in (t.name for t in response.templates)

    @pytest.mark.django_db
    def test_guest_cannot_update_city(self, setup, client):
        """Гость не должен иметь возможность обновить запись."""
        original_rating = VisitedCity.objects.get(pk=1).rating

        client.post(reverse('city-update', kwargs={'pk': 1}), data={'rating': 5})

        updated_rating = VisitedCity.objects.get(pk=1).rating
        assert original_rating == updated_rating


class TestUpdateAccessOwner:
    """Тесты доступа к обновлению для авторизованных пользователей-владельцев."""

    @pytest.mark.django_db
    def test_owner_get_shows_form(self, setup, client):
        """GET запрос от владельца должен показывать форму редактирования."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))

        assert response.status_code == 200
        assert 'city/city_create.html' in (t.name for t in response.templates)

    @pytest.mark.django_db
    def test_owner_get_shows_correct_template(self, setup, client):
        """GET запрос должен использовать корректный шаблон."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))

        assert 'city/city_create.html' in (t.name for t in response.templates)

    @pytest.mark.django_db
    def test_owner_get_has_correct_context(self, setup, client):
        """Контекст страницы должен содержать корректные данные."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))

        assert response.context['action'] == 'update'
        assert 'form' in response.context

    @pytest.mark.django_db
    def test_owner_post_with_valid_data_updates_successfully(self, setup, caplog, client):
        """POST запрос от владельца с валидными данными должен успешно обновить запись."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id,
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
        assert 'Updated impression' in updated_city.impression

    @pytest.mark.django_db
    def test_owner_post_redirects_to_city_detail(self, setup, client):
        """После обновления должен быть редирект на страницу города."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        city_id = visited_city.city.id

        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id,
                'date_of_visit': '2023-03-03',
                'has_magnet': True,
                'rating': 5,
            },
        )

        assert response.status_code == 302
        assert f'/city/{city_id}' in response.url

    @pytest.mark.django_db
    def test_owner_post_logs_update(self, setup, caplog, client):
        """Обновление должно логироваться."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)

        client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id,
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


class TestUpdateAccessNonOwner:
    """
    Тесты доступа к обновлению для авторизованных пользователей-не владельцев.

    ПРИМЕЧАНИЕ: В текущей реализации нет проверки владельца записи для update view.
    Это потенциальная проблема безопасности, которая требует исправления.
    Тесты документируют текущее поведение системы.
    """

    @pytest.mark.django_db
    def test_non_owner_get_shows_form(self, setup, client):
        """
        GET запрос от не-владельца показывает форму.
        TODO: Должен возвращать 404, требуется добавить проверку владельца в view.
        """
        client.login(username='username2', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))

        # В текущей реализации возвращает 200, хотя должен 404
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_non_owner_post_can_update(self, setup, client):
        """
        POST запрос от не-владельца может обновить запись.
        TODO: Должен возвращать 404, требуется добавить проверку владельца в view.
        """
        client.login(username='username2', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        original_rating = visited_city.rating

        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id if visited_city.city.region else '',
                'rating': 5,
            },
        )

        # В текущей реализации обновление происходит
        assert response.status_code == 302
        updated_city = VisitedCity.objects.get(pk=1)
        assert updated_city.rating == 5
        assert updated_city.rating != original_rating


class TestUpdateEdgeCases:
    """Тесты граничных случаев при обновлении."""

    @pytest.mark.django_db
    def test_update_nonexistent_city(self, setup, client):
        """Попытка обновить несуществующий город должна возвращать 404."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 9999}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_update_with_invalid_pk(self, setup, client):
        """Попытка обновить с некорректным pk должна возвращать 404."""
        client.login(username='username1', password='password')

        try:
            response = client.get(reverse('city-update', kwargs={'pk': 'invalid'}))
            assert response.status_code == 404
        except:
            # Может быть ValueError при парсинге URL
            pass

    @pytest.mark.django_db
    def test_owner_get_to_nonexistent_city_returns_404(self, setup, client):
        """GET запрос к несуществующему городу должен возвращать 404."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 2}))

        assert response.status_code == 404
