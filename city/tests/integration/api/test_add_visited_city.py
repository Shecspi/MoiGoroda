# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Регрессии совместимого DMR endpoint ``/api/city/visited/add``."""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from rest_framework import status
from typing import Type


@pytest.mark.integration
class TestAddVisitedCityAccess:
    """Проверяет доступ и разрешённые методы без обращения к базе."""

    url = reverse('api__add_visited_city')

    def test_guest_cannot_access(self, client: Client) -> None:
        """Ломается, если DMR миграция открывает создание гостю."""
        response = client.post(self.url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

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

    def test_session_post_requires_csrf_token(
        self, django_user_model: Type[User]
    ) -> None:
        """Ломается, если DMR create controller обходит CSRF session-auth защиты."""
        user = django_user_model.objects.create_user(username='csrf-user', password='password')
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)

        response = client.post(self.url, {'city': 1, 'date_of_visit': '2024-01-15', 'rating': 5})

        assert response.status_code == status.HTTP_403_FORBIDDEN
