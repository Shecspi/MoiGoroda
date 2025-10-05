"""
Мок-тесты для сервиса CitySearchService.

Покрывает:
- Поиск городов по подстроке
- Фильтрацию по коду страны
- Обработку пустых результатов
- Валидацию входных параметров
- Оптимизацию запросов к БД

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from unittest.mock import MagicMock, patch
from django.db.models import QuerySet

from city.services.search import CitySearchService


class TestCitySearchService:
    """Тесты для сервиса CitySearchService."""

    def _setup_mocks_for_search(
        self, mock_city_objects: MagicMock
    ) -> tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock, MagicMock]:
        """Вспомогательная функция для настройки моков для поиска."""
        mock_queryset = MagicMock(spec=QuerySet)
        mock_select_related = MagicMock()
        mock_filter = MagicMock()
        mock_annotate = MagicMock()
        mock_order_by = MagicMock()

        mock_city_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filter
        mock_filter.annotate.return_value = mock_annotate
        mock_annotate.order_by.return_value = mock_order_by
        mock_order_by.__getitem__.return_value = mock_queryset

        return (
            mock_queryset,
            mock_select_related,
            mock_filter,
            mock_annotate,
            mock_order_by,
            mock_queryset,
        )

    @patch('city.services.search.City.objects')
    def test_search_cities_basic_query(self, mock_city_objects: MagicMock) -> None:
        """Тест базового поиска городов по подстроке."""
        # Настройка моков
        mock_queryset = MagicMock(spec=QuerySet)
        mock_select_related = MagicMock()
        mock_filter = MagicMock()
        mock_annotate = MagicMock()
        mock_order_by = MagicMock()

        mock_city_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filter
        mock_filter.annotate.return_value = mock_annotate
        mock_annotate.order_by.return_value = mock_order_by
        mock_order_by.__getitem__.return_value = mock_queryset

        # Выполнение теста
        result = CitySearchService.search_cities('Moscow')

        # Проверки
        mock_city_objects.select_related.assert_called_once_with('region__country')
        mock_select_related.filter.assert_called_once_with(title__icontains='Moscow')
        mock_filter.annotate.assert_called_once()
        mock_annotate.order_by.assert_called_once()
        mock_order_by.__getitem__.assert_called_once_with(slice(None, 50))
        assert result == mock_queryset

    @patch('city.services.search.City.objects')
    def test_search_cities_with_country_filter(self, mock_city_objects: MagicMock) -> None:
        """Тест поиска городов с фильтрацией по стране."""
        # Настройка моков
        mock_queryset = MagicMock(spec=QuerySet)
        mock_select_related = MagicMock()
        mock_filter = MagicMock()
        mock_annotate = MagicMock()
        mock_order_by = MagicMock()
        mock_country_filter = MagicMock()

        mock_city_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filter
        mock_filter.annotate.return_value = mock_annotate
        mock_annotate.order_by.return_value = mock_order_by
        mock_order_by.filter.return_value = mock_country_filter
        mock_country_filter.__getitem__.return_value = mock_queryset

        # Выполнение теста
        result = CitySearchService.search_cities('Moscow', country='RU')

        # Проверки
        mock_city_objects.select_related.assert_called_once_with('region__country')
        mock_select_related.filter.assert_called_once_with(title__icontains='Moscow')
        mock_filter.annotate.assert_called_once()
        mock_annotate.order_by.assert_called_once()
        mock_order_by.filter.assert_called_once_with(region__country__code='RU')
        mock_country_filter.__getitem__.assert_called_once_with(slice(None, 50))
        assert result == mock_queryset

    @patch('city.services.search.City.objects')
    def test_search_cities_with_custom_limit(self, mock_city_objects: MagicMock) -> None:
        """Тест поиска городов с пользовательским лимитом."""
        # Настройка моков
        mock_queryset = MagicMock(spec=QuerySet)
        mock_select_related = MagicMock()
        mock_filter = MagicMock()
        mock_annotate = MagicMock()
        mock_order_by = MagicMock()

        mock_city_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filter
        mock_filter.annotate.return_value = mock_annotate
        mock_annotate.order_by.return_value = mock_order_by
        mock_order_by.__getitem__.return_value = mock_queryset

        # Выполнение теста с пользовательским лимитом
        result = CitySearchService.search_cities('Moscow', limit=20)

        # Проверки
        mock_city_objects.select_related.assert_called_once_with('region__country')
        mock_select_related.filter.assert_called_once_with(title__icontains='Moscow')
        mock_filter.annotate.assert_called_once()
        mock_annotate.order_by.assert_called_once()
        mock_order_by.__getitem__.assert_called_once_with(slice(None, 20))
        assert result == mock_queryset

    @patch('city.services.search.City.objects')
    def test_search_cities_without_country_filter(self, mock_city_objects: MagicMock) -> None:
        """Тест поиска городов без фильтрации по стране."""
        # Настройка моков
        (
            mock_queryset,
            mock_select_related,
            mock_filter,
            mock_annotate,
            mock_order_by,
            mock_result,
        ) = self._setup_mocks_for_search(mock_city_objects)

        # Выполнение теста
        result = CitySearchService.search_cities('London', country=None)

        # Проверки
        mock_city_objects.select_related.assert_called_once_with('region__country')
        mock_select_related.filter.assert_called_once_with(title__icontains='London')
        mock_filter.annotate.assert_called_once()
        mock_annotate.order_by.assert_called_once()
        mock_order_by.__getitem__.assert_called_once_with(slice(None, 50))
        assert result == mock_result

    @patch('city.services.search.City.objects')
    def test_search_cities_empty_query(self, mock_city_objects: MagicMock) -> None:
        """Тест поиска с пустой строкой запроса."""
        # Настройка моков
        (
            mock_queryset,
            mock_select_related,
            mock_filter,
            mock_annotate,
            mock_order_by,
            mock_result,
        ) = self._setup_mocks_for_search(mock_city_objects)

        # Выполнение теста
        result = CitySearchService.search_cities('')

        # Проверки
        mock_city_objects.select_related.assert_called_once_with('region__country')
        mock_select_related.filter.assert_called_once_with(title__icontains='')
        mock_filter.annotate.assert_called_once()
        mock_annotate.order_by.assert_called_once()
        mock_order_by.__getitem__.assert_called_once_with(slice(None, 50))
        assert result == mock_result

    @patch('city.services.search.City.objects')
    def test_search_cities_special_characters_in_query(self, mock_city_objects: MagicMock) -> None:
        """Тест поиска с специальными символами в запросе."""
        # Настройка моков
        (
            mock_queryset,
            mock_select_related,
            mock_filter,
            mock_annotate,
            mock_order_by,
            mock_result,
        ) = self._setup_mocks_for_search(mock_city_objects)

        # Выполнение теста
        special_query = 'São Paulo!@#$%^&*()'
        result = CitySearchService.search_cities(special_query)

        # Проверки
        mock_city_objects.select_related.assert_called_once_with('region__country')
        mock_select_related.filter.assert_called_once_with(title__icontains=special_query)
        mock_filter.annotate.assert_called_once()
        mock_annotate.order_by.assert_called_once()
        mock_order_by.__getitem__.assert_called_once_with(slice(None, 50))
        assert result == mock_result

    @patch('city.services.search.City.objects')
    def test_search_cities_unicode_query(self, mock_city_objects: MagicMock) -> None:
        """Тест поиска с Unicode символами в запросе."""
        # Настройка моков
        (
            mock_queryset,
            mock_select_related,
            mock_filter,
            mock_annotate,
            mock_order_by,
            mock_result,
        ) = self._setup_mocks_for_search(mock_city_objects)

        # Выполнение теста
        unicode_query = 'Москва'
        result = CitySearchService.search_cities(unicode_query)

        # Проверки
        mock_city_objects.select_related.assert_called_once_with('region__country')
        mock_select_related.filter.assert_called_once_with(title__icontains=unicode_query)
        mock_filter.annotate.assert_called_once()
        mock_annotate.order_by.assert_called_once()
        mock_order_by.__getitem__.assert_called_once_with(slice(None, 50))
        assert result == mock_result
