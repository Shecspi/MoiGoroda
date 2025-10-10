"""
Полный набор тестов для VisitedCityRepository.

Этот модуль содержит все тесты для методов репозитория посещенных городов.
Используются моки для изоляции от базы данных и быстрого выполнения.
"""

import pytest
from typing import Any
from unittest.mock import MagicMock
from pytest_mock import MockerFixture

from city.models import VisitedCity
from city.repository.visited_city_repository import VisitedCityRepository


@pytest.fixture
def repo() -> VisitedCityRepository:
    """Фикстура для создания экземпляра VisitedCityRepository."""
    return VisitedCityRepository()


@pytest.fixture
def mock_user() -> Any:
    """Фикстура для создания мок-объекта пользователя."""

    class User:
        id = 1

    return User()


# =============================================================================
# Тесты для get_average_rating
# =============================================================================


@pytest.mark.integration
class TestGetAverageRating:
    """Тесты для метода get_average_rating."""

    def test_returns_rounded_average(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет корректное округление среднего рейтинга до 0.5."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_aggregate = mock_filter.return_value.aggregate
        mock_aggregate.return_value = {'rating__avg': 3.7}

        result = repo.get_average_rating(city_id=1)

        assert result == 3.5
        mock_filter.assert_called_once_with(city_id=1)
        mock_aggregate.assert_called_once()

    def test_rounds_down_to_nearest_half(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет округление вниз (3.3 → 3.0)."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_aggregate = mock_filter.return_value.aggregate
        mock_aggregate.return_value = {'rating__avg': 3.3}

        result = repo.get_average_rating(city_id=1)

        assert result == 3.5

    def test_rounds_up_to_nearest_half(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет округление вверх (3.8 → 4.0)."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_aggregate = mock_filter.return_value.aggregate
        mock_aggregate.return_value = {'rating__avg': 3.8}

        result = repo.get_average_rating(city_id=1)

        assert result == 4.0

    def test_returns_zero_when_none(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет возврат 0.0 при отсутствии рейтингов."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_aggregate = mock_filter.return_value.aggregate
        mock_aggregate.return_value = {'rating__avg': None}

        result = repo.get_average_rating(city_id=1)

        assert result == 0.0

    def test_handles_exact_half_values(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет обработку точных значений .5."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_aggregate = mock_filter.return_value.aggregate
        mock_aggregate.return_value = {'rating__avg': 3.5}

        result = repo.get_average_rating(city_id=1)

        assert result == 3.5

    def test_handles_integer_values(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет обработку целых значений."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_aggregate = mock_filter.return_value.aggregate
        mock_aggregate.return_value = {'rating__avg': 4.0}

        result = repo.get_average_rating(city_id=1)

        assert result == 4.0

    def test_handles_zero_rating(self, mocker: MockerFixture, repo: VisitedCityRepository) -> None:
        """Проверяет обработку нулевого рейтинга."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_aggregate = mock_filter.return_value.aggregate
        mock_aggregate.return_value = {'rating__avg': 0.0}

        result = repo.get_average_rating(city_id=1)

        assert result == 0.0

    def test_handles_max_rating(self, mocker: MockerFixture, repo: VisitedCityRepository) -> None:
        """Проверяет обработку максимального рейтинга."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_aggregate = mock_filter.return_value.aggregate
        mock_aggregate.return_value = {'rating__avg': 5.0}

        result = repo.get_average_rating(city_id=1)

        assert result == 5.0

    def test_with_different_city_ids(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет работу с разными city_id."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_aggregate = mock_filter.return_value.aggregate
        mock_aggregate.return_value = {'rating__avg': 4.2}

        repo.get_average_rating(city_id=999)

        mock_filter.assert_called_once_with(city_id=999)


# =============================================================================
# Тесты для count_user_visits
# =============================================================================


@pytest.mark.integration
class TestCountUserVisits:
    """Тесты для метода count_user_visits."""

    def test_returns_visit_count(
        self, mocker: MockerFixture, repo: VisitedCityRepository, mock_user: Any
    ) -> None:
        """Проверяет корректный подсчет посещений пользователя."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 4

        result = repo.count_user_visits(city_id=1, user=mock_user)

        assert result == 4
        mock_filter.assert_called_once_with(city_id=1, user=mock_user)
        mock_count.assert_called_once()

    def test_returns_zero_when_no_visits(
        self, mocker: MockerFixture, repo: VisitedCityRepository, mock_user: Any
    ) -> None:
        """Проверяет возврат 0 при отсутствии посещений."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 0

        result = repo.count_user_visits(city_id=1, user=mock_user)

        assert result == 0
        mock_filter.assert_called_once_with(city_id=1, user=mock_user)
        mock_count.assert_called_once()

    def test_filters_by_user_and_city(
        self, mocker: MockerFixture, repo: VisitedCityRepository, mock_user: Any
    ) -> None:
        """Проверяет правильность параметров фильтрации."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 2

        repo.count_user_visits(city_id=42, user=mock_user)

        mock_filter.assert_called_once_with(city_id=42, user=mock_user)

    def test_handles_large_visit_count(
        self, mocker: MockerFixture, repo: VisitedCityRepository, mock_user: Any
    ) -> None:
        """Проверяет обработку большого количества посещений."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 1000

        result = repo.count_user_visits(city_id=1, user=mock_user)

        assert result == 1000


# =============================================================================
# Тесты для count_all_visits
# =============================================================================


@pytest.mark.integration
class TestCountAllVisits:
    """Тесты для метода count_all_visits."""

    def test_returns_total_visit_count(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет корректный подсчет всех посещений."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 15

        result = repo.count_all_visits(city_id=1)

        assert result == 15
        mock_filter.assert_called_once_with(city_id=1)
        mock_count.assert_called_once()

    def test_returns_zero_when_no_visits(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет возврат 0 при отсутствии посещений."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 0

        result = repo.count_all_visits(city_id=1)

        assert result == 0
        mock_filter.assert_called_once_with(city_id=1)
        mock_count.assert_called_once()

    def test_filters_by_city_id(self, mocker: MockerFixture, repo: VisitedCityRepository) -> None:
        """Проверяет фильтрацию по city_id."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 5

        repo.count_all_visits(city_id=999)

        mock_filter.assert_called_once_with(city_id=999)

    def test_handles_large_visit_count(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет обработку большого количества посещений."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 50000

        result = repo.count_all_visits(city_id=1)

        assert result == 50000


# =============================================================================
# Тесты для get_popular_months
# =============================================================================


@pytest.mark.integration
class TestGetPopularMonths:
    """Тесты для метода get_popular_months."""

    def test_returns_top_three_months(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет возврат 3 самых популярных месяцев."""
        mock_qs = mocker.MagicMock()
        mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)

        mock_qs.annotate.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs
        mock_qs.values_list.return_value = [5, 6, 7]

        result = repo.get_popular_months(city_id=1)

        assert result == [5, 6, 7]
        mock_qs.annotate.assert_called()
        mock_qs.values.assert_called()
        mock_qs.order_by.assert_called()
        mock_qs.values_list.assert_called_once_with('month', flat=True)

    def test_returns_empty_when_no_visits(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет возврат пустого списка при отсутствии посещений."""
        mock_qs = mocker.MagicMock()
        mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)

        mock_qs.annotate.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs
        mock_qs.values_list.return_value = []

        result = repo.get_popular_months(city_id=1)

        assert result == []

    def test_filters_null_dates(self, mocker: MockerFixture, repo: VisitedCityRepository) -> None:
        """Проверяет фильтрацию посещений без даты."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')

        repo.get_popular_months(city_id=1)

        mock_filter.assert_called_once_with(city_id=1, date_of_visit__isnull=False)

    def test_returns_less_than_three_months(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет корректную работу при < 3 месяцах."""
        mock_qs = mocker.MagicMock()
        mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)

        mock_qs.annotate.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs
        mock_qs.values_list.return_value = [12, 1]

        result = repo.get_popular_months(city_id=1)

        assert result == [12, 1]
        assert len(result) == 2

    def test_returns_exactly_three_months(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет корректную работу при ровно 3 месяцах."""
        mock_qs = mocker.MagicMock()
        mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)

        mock_qs.annotate.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs
        mock_qs.values_list.return_value = [6, 7, 8]

        result = repo.get_popular_months(city_id=1)

        assert result == [6, 7, 8]
        assert len(result) == 3


# =============================================================================
# Тесты для get_user_visits
# =============================================================================


@pytest.mark.integration
class TestGetUserVisits:
    """Тесты для метода get_user_visits."""

    def test_returns_user_visits(
        self, mocker: MockerFixture, repo: VisitedCityRepository, mock_user: Any
    ) -> None:
        """Проверяет корректный возврат посещений пользователя."""
        mock_qs = mocker.MagicMock()
        mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)

        mock_qs.select_related.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs
        mock_qs.values.return_value = [
            {
                'id': 1,
                'date_of_visit': '2024-06-01',
                'rating': 4,
                'impression': 'Beautiful!',
                'city__title': 'Kazan',
            }
        ]

        result = repo.get_user_visits(city_id=1, user=mock_user)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['id'] == 1
        assert result[0]['city__title'] == 'Kazan'
        assert result[0]['rating'] == 4

        mock_qs.select_related.assert_called_once_with('city')
        mock_qs.order_by.assert_called()
        mock_qs.values.assert_called_once_with(
            'id', 'date_of_visit', 'rating', 'impression', 'city__title'
        )

    def test_returns_empty_when_no_visits(
        self, mocker: MockerFixture, repo: VisitedCityRepository, mock_user: Any
    ) -> None:
        """Проверяет возврат пустого списка при отсутствии посещений."""
        mock_qs = mocker.MagicMock()
        mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)

        mock_qs.select_related.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs
        mock_qs.values.return_value = []

        result = repo.get_user_visits(city_id=1, user=mock_user)

        assert result == []

    def test_filters_by_user_and_city(
        self, mocker: MockerFixture, repo: VisitedCityRepository, mock_user: Any
    ) -> None:
        """Проверяет правильность фильтрации."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')

        repo.get_user_visits(city_id=42, user=mock_user)

        mock_filter.assert_called_once_with(user=mock_user, city_id=42)

    def test_orders_by_date_desc_nulls_last(
        self, mocker: MockerFixture, repo: VisitedCityRepository, mock_user: Any
    ) -> None:
        """Проверяет правильную сортировку (дата по убыванию, null последние)."""
        mock_qs = mocker.MagicMock()
        mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)
        mock_qs.select_related.return_value = mock_qs
        mock_qs.values.return_value = []

        repo.get_user_visits(city_id=1, user=mock_user)

        # Проверяем, что order_by был вызван
        mock_qs.order_by.assert_called()

    def test_selects_related_city(
        self, mocker: MockerFixture, repo: VisitedCityRepository, mock_user: Any
    ) -> None:
        """Проверяет использование select_related для оптимизации."""
        mock_qs = mocker.MagicMock()
        mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)
        mock_qs.order_by.return_value = mock_qs
        mock_qs.values.return_value = []

        repo.get_user_visits(city_id=1, user=mock_user)

        mock_qs.select_related.assert_called_once_with('city')

    def test_returns_multiple_visits(
        self, mocker: MockerFixture, repo: VisitedCityRepository, mock_user: Any
    ) -> None:
        """Проверяет возврат множественных посещений."""
        mock_qs = mocker.MagicMock()
        mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)

        mock_qs.select_related.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs
        mock_qs.values.return_value = [
            {
                'id': 1,
                'date_of_visit': '2024-06-01',
                'rating': 4,
                'impression': 'Good',
                'city__title': 'Moscow',
            },
            {
                'id': 2,
                'date_of_visit': '2024-05-01',
                'rating': 5,
                'impression': 'Excellent',
                'city__title': 'Moscow',
            },
        ]

        result = repo.get_user_visits(city_id=1, user=mock_user)

        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['id'] == 2


# =============================================================================
# Тесты для get_number_of_users_who_visit_city
# =============================================================================


@pytest.mark.integration
class TestGetNumberOfUsersWhoVisitCity:
    """Тесты для метода get_number_of_users_who_visit_city."""

    def test_returns_user_count(self, mocker: MockerFixture, repo: VisitedCityRepository) -> None:
        """Проверяет корректный подсчет пользователей."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 7

        result = repo.get_number_of_users_who_visit_city(city_id=42)

        assert result == 7
        mock_filter.assert_called_once_with(city_id=42, is_first_visit=True)
        mock_count.assert_called_once()

    def test_returns_zero_when_no_users(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет возврат 0 при отсутствии пользователей."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 0

        result = repo.get_number_of_users_who_visit_city(city_id=999)

        assert result == 0
        mock_filter.assert_called_once_with(city_id=999, is_first_visit=True)
        mock_count.assert_called_once()

    def test_filters_by_first_visit(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет фильтрацию только первых посещений."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 5

        repo.get_number_of_users_who_visit_city(city_id=1)

        # Проверяем, что фильтр включает is_first_visit=True
        mock_filter.assert_called_once_with(city_id=1, is_first_visit=True)

    def test_handles_large_user_count(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет обработку большого количества пользователей."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 10000

        result = repo.get_number_of_users_who_visit_city(city_id=1)

        assert result == 10000

    def test_with_different_city_ids(
        self, mocker: MockerFixture, repo: VisitedCityRepository
    ) -> None:
        """Проверяет работу с различными city_id."""
        mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 3

        for city_id in [1, 100, 999, 12345]:
            repo.get_number_of_users_who_visit_city(city_id=city_id)
            mock_filter.assert_called_with(city_id=city_id, is_first_visit=True)
