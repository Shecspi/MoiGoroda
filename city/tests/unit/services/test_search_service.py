"""
Unit тесты для CitySearchService (city/services/search.py).

Проверяется:
- Логика поиска с различными параметрами
- Приоритизация результатов
- Фильтрация по стране
- Ограничение количества результатов
"""

from unittest.mock import MagicMock, patch

import pytest

from city.services.search import CitySearchService


@pytest.mark.unit
class TestCitySearchServiceBasic:
    """Базовые тесты поиска городов."""

    @patch('city.services.search.City.objects')
    def test_search_cities_basic_query(self, mock_city_objects: MagicMock) -> None:
        """Базовый поиск по query."""
        mock_queryset = MagicMock()
        mock_city_objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)

        CitySearchService.search_cities(query='Москва')

        # Проверяем что был вызван select_related для оптимизации
        mock_city_objects.select_related.assert_called_once_with('region__country')

        # Проверяем фильтрацию по названию
        mock_queryset.filter.assert_called_once_with(title__icontains='Москва')

    @patch('city.services.search.City.objects')
    def test_search_cities_with_country_filter(self, mock_city_objects: MagicMock) -> None:
        """Поиск с фильтрацией по стране."""
        mock_queryset = MagicMock()
        mock_city_objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)

        CitySearchService.search_cities(query='Москва', country='RU')

        # Должно быть два вызова filter: по title и по country
        assert mock_queryset.filter.call_count == 2

        # Второй вызов - фильтр по стране
        second_call = mock_queryset.filter.call_args_list[1]
        assert 'region__country__code' in str(second_call)

    @patch('city.services.search.City.objects')
    def test_search_cities_without_country_filter(self, mock_city_objects: MagicMock) -> None:
        """Поиск без фильтрации по стране."""
        mock_queryset = MagicMock()
        mock_city_objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)

        CitySearchService.search_cities(query='Москва', country=None)

        # Должен быть только один вызов filter (по title)
        assert mock_queryset.filter.call_count == 1

    @patch('city.services.search.City.objects')
    def test_search_cities_applies_limit(self, mock_city_objects: MagicMock) -> None:
        """Применяется ограничение на количество результатов."""
        mock_queryset = MagicMock()
        mock_city_objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value='limited_queryset')

        CitySearchService.search_cities(query='Москва', limit=10)

        # Проверяем что был применён slice [:10]
        mock_queryset.__getitem__.assert_called_once_with(slice(None, 10, None))

    @patch('city.services.search.City.objects')
    def test_search_cities_default_limit_is_50(self, mock_city_objects: MagicMock) -> None:
        """По умолчанию лимит 50."""
        mock_queryset = MagicMock()
        mock_city_objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)

        CitySearchService.search_cities(query='Москва')

        # Проверяем лимит 50
        mock_queryset.__getitem__.assert_called_once_with(slice(None, 50, None))


@pytest.mark.unit
class TestCitySearchServicePrioritization:
    """Тесты приоритизации результатов поиска."""

    @patch('city.services.search.City.objects')
    def test_search_applies_priority_annotation(self, mock_city_objects: MagicMock) -> None:
        """Поиск применяет аннотацию для приоритизации."""
        mock_queryset = MagicMock()
        mock_city_objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)

        CitySearchService.search_cities(query='Мос')

        # Проверяем что была вызвана annotate
        assert mock_queryset.annotate.called
        mock_queryset.order_by.assert_called_once_with('search_priority', 'title')

    @patch('city.services.search.City.objects')
    def test_search_orders_by_priority_then_title(self, mock_city_objects: MagicMock) -> None:
        """Сортировка сначала по приоритету, затем по названию."""
        mock_queryset = MagicMock()
        mock_city_objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)

        CitySearchService.search_cities(query='Москва')

        mock_queryset.order_by.assert_called_once_with('search_priority', 'title')


@pytest.mark.unit
class TestCitySearchServiceEdgeCases:
    """Тесты граничных случаев."""

    @patch('city.services.search.City.objects')
    def test_search_with_empty_query(self, mock_city_objects: MagicMock) -> None:
        """Поиск с пустой строкой."""
        mock_queryset = MagicMock()
        mock_city_objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)

        CitySearchService.search_cities(query='')

        # Должен отработать фильтр даже с пустой строкой
        mock_queryset.filter.assert_called_once_with(title__icontains='')

    @patch('city.services.search.City.objects')
    def test_search_with_zero_limit(self, mock_city_objects: MagicMock) -> None:
        """Поиск с лимитом 0."""
        mock_queryset = MagicMock()
        mock_city_objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)

        CitySearchService.search_cities(query='Москва', limit=0)

        mock_queryset.__getitem__.assert_called_once_with(slice(None, 0, None))

    @patch('city.services.search.City.objects')
    def test_search_with_large_limit(self, mock_city_objects: MagicMock) -> None:
        """Поиск с большим лимитом."""
        mock_queryset = MagicMock()
        mock_city_objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)

        CitySearchService.search_cities(query='Москва', limit=1000)

        mock_queryset.__getitem__.assert_called_once_with(slice(None, 1000, None))

    @patch('city.services.search.City.objects')
    def test_search_with_special_characters(self, mock_city_objects: MagicMock) -> None:
        """Поиск со специальными символами."""
        mock_queryset = MagicMock()
        mock_city_objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = MagicMock(return_value=mock_queryset)

        CitySearchService.search_cities(query='Санкт-Петербург')

        mock_queryset.filter.assert_called_once_with(title__icontains='Санкт-Петербург')
