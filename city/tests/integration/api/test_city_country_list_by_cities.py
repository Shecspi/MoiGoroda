# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Контрактные тесты списка стран с городами из city API."""

from unittest.mock import MagicMock, patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestCityCountryListByCities:
    """Проверяет неизменный компактный response city lookup endpoint-а."""

    url = reverse('api__country_list_by_cities')

    @patch('city.api.lookups.Country.objects.filter')
    def test_returns_sorted_compact_country_items(
        self,
        mock_filter: MagicMock,
        api_client: APIClient,
    ) -> None:
        country = MagicMock()
        country.id = 1
        country.code = 'RU'
        country.name = 'Россия'
        queryset = MagicMock()
        mock_filter.return_value = queryset
        queryset.distinct.return_value.order_by.return_value = [country]

        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        mock_filter.assert_called_once_with(city__isnull=False)
        queryset.distinct.return_value.order_by.assert_called_once_with('name')
        assert response.json() == [{'id': 1, 'code': 'RU', 'name': 'Россия'}]
