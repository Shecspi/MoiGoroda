"""
Тесты для эндпоинта /api/city/visited/subscriptions (GetVisitedCitiesFromSubscriptions).

Покрывает:
- Получение посещенных городов из подписок
- Валидацию user_ids параметров
- Проверку подписок и разрешений пользователей
- Особые права суперпользователя
- Обработку пустых списков пользователей

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from unittest.mock import MagicMock, patch
import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from account.models import ShareSettings


class TestGetVisitedCitiesFromSubscriptions:
    """Тесты для эндпоинта /api/city/visited/subscriptions (GetVisitedCitiesFromSubscriptions)."""

    url: str = reverse('api__get_visited_cities_from_subscriptions')

    def test_guest_cannot_access(self, api_client: APIClient) -> None:
        """Проверяет, что неавторизованные пользователи не могут получить доступ к эндпоинту."""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
    def test_prohibited_methods(
        self, api_client: APIClient, authenticated_user: User, method: str
    ) -> None:
        """Проверяет, что запрещенные HTTP методы возвращают 405."""
        client_method = getattr(api_client, method)
        response = client_method(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @patch('city.api.logger')
    def test_invalid_user_ids_format(
        self, mock_logger: MagicMock, api_client: APIClient, authenticated_user: User
    ) -> None:
        """Проверяет обработку некорректного формата user_ids."""
        response = api_client.get(f'{self.url}?user_ids=invalid,ids')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_logger.warning.assert_called_once()

    @patch('city.api.get_unique_visited_cities')
    @patch('city.api.logger')
    def test_empty_user_ids(
        self,
        mock_logger: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        api_client: APIClient,
        authenticated_user: User,
    ) -> None:
        """Проверяет обработку пустого списка user_ids."""
        # Пустой список user_ids должен приводить к ошибке валидации
        response = api_client.get(f'{self.url}?user_ids=')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('city.api.get_unique_visited_cities')
    @patch('subscribe.repository.is_subscribed')
    @patch('account.models.ShareSettings.objects.get')
    @patch('city.api.logger')
    def test_superuser_bypasses_restrictions(
        self,
        mock_logger: MagicMock,
        mock_share_settings: MagicMock,
        mock_is_subscribed: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        api_client: APIClient,
        superuser: User,
        mock_visited_city: MagicMock,
    ) -> None:
        """Проверяет, что суперпользователь может обходить ограничения подписок."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__.return_value = [mock_visited_city]
        mock_get_unique_visited_cities.return_value = mock_queryset

        # Используем валидные user_ids
        response = api_client.get(f'{self.url}?user_ids=1')

        assert response.status_code == status.HTTP_200_OK
        mock_logger.info.assert_called_once()
        # Superuser bypasses subscription checks
        mock_is_subscribed.assert_not_called()
        mock_share_settings.assert_not_called()

    @patch('city.api.get_unique_visited_cities')
    @patch('subscribe.repository.is_subscribed')
    @patch('account.models.ShareSettings.objects.get')
    @patch('city.api.logger')
    def test_user_without_subscription_access_denied(
        self,
        mock_logger: MagicMock,
        mock_share_settings: MagicMock,
        mock_is_subscribed: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        api_client: APIClient,
        authenticated_user: User,
    ) -> None:
        """Проверяет, что пользователи без подписки не могут получить доступ к данным."""
        mock_share_settings.side_effect = ShareSettings.DoesNotExist()
        mock_is_subscribed.return_value = False

        response = api_client.get(f'{self.url}?user_ids=999')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
