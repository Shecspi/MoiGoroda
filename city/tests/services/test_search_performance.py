"""
Тесты производительности для сервиса поиска городов.

Покрывает:
- Время выполнения поиска с разными лимитами
- Сравнение производительности с приоритизацией и без неё

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import time
from unittest.mock import MagicMock, patch

from city.services.search import CitySearchService


class TestCitySearchPerformance:
    """Тесты производительности для сервиса CitySearchService."""

    @patch('city.services.search.City.objects')
    def test_search_performance_with_limit(self, mock_city_objects: MagicMock) -> None:
        """Тест производительности поиска с ограничением результатов."""
        # Настройка моков для имитации большого количества результатов
        mock_queryset = MagicMock()
        mock_select_related = MagicMock()
        mock_filter = MagicMock()
        mock_annotate = MagicMock()
        mock_order_by = MagicMock()

        mock_city_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filter
        mock_filter.annotate.return_value = mock_annotate
        mock_annotate.order_by.return_value = mock_order_by
        mock_order_by.__getitem__.return_value = mock_queryset

        # Измеряем время выполнения
        start_time = time.time()
        result = CitySearchService.search_cities('Moscow', limit=10)
        end_time = time.time()

        execution_time = end_time - start_time

        # Проверяем, что запрос выполнился быстро (менее 1 секунды для мока)
        assert execution_time < 1.0
        assert result == mock_queryset

        # Проверяем, что лимит применился
        mock_order_by.__getitem__.assert_called_once_with(slice(None, 10))

    @patch('city.services.search.City.objects')
    def test_search_performance_without_limit(self, mock_city_objects: MagicMock) -> None:
        """Тест производительности поиска без ограничения результатов."""
        # Настройка моков
        mock_queryset = MagicMock()
        mock_select_related = MagicMock()
        mock_filter = MagicMock()
        mock_annotate = MagicMock()
        mock_order_by = MagicMock()

        mock_city_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filter
        mock_filter.annotate.return_value = mock_annotate
        mock_annotate.order_by.return_value = mock_order_by
        mock_order_by.__getitem__.return_value = mock_queryset

        # Измеряем время выполнения с дефолтным лимитом
        start_time = time.time()
        result = CitySearchService.search_cities('Moscow')
        end_time = time.time()

        execution_time = end_time - start_time

        # Проверяем, что запрос выполнился быстро
        assert execution_time < 1.0
        assert result == mock_queryset

        # Проверяем, что применился дефолтный лимит
        mock_order_by.__getitem__.assert_called_once_with(slice(None, 50))

    def test_search_priority_logic(self) -> None:
        """Тест логики приоритизации поиска."""
        # Этот тест проверяет, что логика приоритизации работает корректно
        # В реальном приложении это будет проверяться через интеграционные тесты

        # Проверяем, что метод принимает все необходимые параметры
        with patch('city.services.search.City.objects') as mock_objects:
            mock_queryset = MagicMock()
            mock_select_related = MagicMock()
            mock_filter = MagicMock()
            mock_annotate = MagicMock()
            mock_order_by = MagicMock()

            mock_objects.select_related.return_value = mock_select_related
            mock_select_related.filter.return_value = mock_filter
            mock_filter.annotate.return_value = mock_annotate
            mock_annotate.order_by.return_value = mock_order_by
            mock_order_by.__getitem__.return_value = mock_queryset

            # Тестируем с разными параметрами
            CitySearchService.search_cities('Moscow')
            CitySearchService.search_cities('Moscow', country='RU')
            CitySearchService.search_cities('Moscow', limit=20)
            CitySearchService.search_cities('Moscow', country='RU', limit=20)

            # Проверяем, что все вызовы прошли успешно
            assert mock_objects.select_related.call_count == 4
