"""
Полный набор тестов для CityRepository.

Этот модуль содержит все тесты для методов репозитория городов.
Используются моки для изоляции от базы данных и быстрого выполнения.
"""

import pytest
from typing import Any
from unittest.mock import Mock, MagicMock

from city.models import City
from city.repository.city_repository import CityRepository


@pytest.fixture
def repo() -> CityRepository:
    """Фикстура для создания экземпляра CityRepository."""
    return CityRepository()


@pytest.fixture
def mock_city() -> Mock:
    """Фикстура для создания мок-объекта City."""
    city = Mock(spec=City)
    city.id = 42
    city.country = Mock(id=1)
    city.region = Mock(id=7)
    return city


# =============================================================================
# Тесты для get_by_id
# =============================================================================


class TestGetById:
    """Тесты для метода get_by_id."""

    def test_returns_city_when_found(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет, что get_by_id возвращает объект City, если город существует."""
        fake_city = mocker.Mock(spec=City)
        mock_get = mocker.patch('city.models.City.objects.get', return_value=fake_city)

        result = repo.get_by_id(city_id=42)

        assert result is fake_city
        mock_get.assert_called_once_with(id=42)

    def test_raises_does_not_exist_when_not_found(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет, что get_by_id выбрасывает City.DoesNotExist, если город не найден."""
        mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

        with pytest.raises(City.DoesNotExist):
            repo.get_by_id(city_id=999)

    def test_raises_multiple_objects_returned(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет, что get_by_id выбрасывает City.MultipleObjectsReturned при дубликатах."""
        mocker.patch('city.models.City.objects.get', side_effect=City.MultipleObjectsReturned)

        with pytest.raises(City.MultipleObjectsReturned):
            repo.get_by_id(city_id=42)

    def test_with_zero_id(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет поведение при передаче id=0."""
        fake_city = mocker.Mock(spec=City)
        mock_get = mocker.patch('city.models.City.objects.get', return_value=fake_city)

        result = repo.get_by_id(city_id=0)

        assert result is fake_city
        mock_get.assert_called_once_with(id=0)

    def test_with_negative_id(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет поведение при передаче отрицательного id."""
        mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

        with pytest.raises(City.DoesNotExist):
            repo.get_by_id(city_id=-1)


# =============================================================================
# Тесты для get_number_of_cities
# =============================================================================


class TestGetNumberOfCities:
    """Тесты для метода get_number_of_cities."""

    def test_without_country_code(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет, что метод возвращает общее количество городов без фильтра."""
        mock_all = mocker.patch('city.models.City.objects.all')
        mock_count = mock_all.return_value.count
        mock_count.return_value = 100

        result = repo.get_number_of_cities()

        assert result == 100
        mock_all.assert_called_once()
        mock_count.assert_called_once()

    def test_with_country_code(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет фильтрацию по коду страны."""
        mock_all = mocker.patch('city.models.City.objects.all')
        mock_filter = mock_all.return_value.filter
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 50

        result = repo.get_number_of_cities(country_code='RU')

        assert result == 50
        mock_all.assert_called_once()
        mock_filter.assert_called_once_with(country__code='RU')
        mock_count.assert_called_once()

    def test_with_empty_country_code(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет, что пустой country_code не применяет фильтр."""
        mock_all = mocker.patch('city.models.City.objects.all')
        mock_count = mock_all.return_value.count
        mock_count.return_value = 75

        result = repo.get_number_of_cities(country_code='')

        assert result == 75
        mock_all.assert_called_once()
        mock_count.assert_called_once()

    def test_returns_zero_when_no_cities(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат 0 при отсутствии городов."""
        mock_all = mocker.patch('city.models.City.objects.all')
        mock_filter = mock_all.return_value.filter
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 0

        result = repo.get_number_of_cities(country_code='ZZ')

        assert result == 0

    def test_with_none_country_code(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет поведение при country_code=None."""
        mock_all = mocker.patch('city.models.City.objects.all')
        mock_count = mock_all.return_value.count
        mock_count.return_value = 100

        result = repo.get_number_of_cities(country_code=None)

        assert result == 100
        mock_all.assert_called_once()
        mock_count.assert_called_once()

    def test_exception_propagates(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет, что исключения из БД пробрасываются."""
        mock_all = mocker.patch('city.models.City.objects.all')
        mock_count = mock_all.return_value.count
        mock_count.side_effect = Exception('DB error')

        with pytest.raises(Exception, match='DB error'):
            repo.get_number_of_cities()


# =============================================================================
# Тесты для get_number_of_cities_in_region_by_city
# =============================================================================


class TestGetNumberOfCitiesInRegionByCity:
    """Тесты для метода get_number_of_cities_in_region_by_city."""

    def test_success_with_region(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет корректный подсчет городов в регионе."""
        city_instance = mocker.Mock()
        city_instance.region = 'region_1'
        mock_get = mocker.patch('city.models.City.objects.get', return_value=city_instance)

        mock_filter = mocker.patch('city.models.City.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 15

        result = repo.get_number_of_cities_in_region_by_city(city_id=123)

        assert result == 15
        mock_get.assert_called_once_with(id=123)
        mock_filter.assert_called_once_with(region=city_instance.region)
        mock_count.assert_called_once()

    def test_returns_zero_when_city_not_found(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат 0 при отсутствии города."""
        mock_get = mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

        result = repo.get_number_of_cities_in_region_by_city(city_id=999)

        assert result == 0
        mock_get.assert_called_once_with(id=999)

    def test_returns_zero_when_multiple_objects(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат 0 при дубликатах."""
        mock_get = mocker.patch(
            'city.models.City.objects.get', side_effect=City.MultipleObjectsReturned
        )

        result = repo.get_number_of_cities_in_region_by_city(city_id=123)

        assert result == 0

    def test_with_none_region(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет обработку города без региона."""
        city_instance = mocker.Mock()
        city_instance.region = None
        mocker.patch('city.models.City.objects.get', return_value=city_instance)

        mock_filter = mocker.patch('city.models.City.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 5

        result = repo.get_number_of_cities_in_region_by_city(city_id=123)

        assert result == 5
        mock_filter.assert_called_once_with(region=None)

    def test_with_zero_cities_in_region(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат 0 при отсутствии городов в регионе."""
        city_instance = mocker.Mock()
        city_instance.region = 'region_1'
        mocker.patch('city.models.City.objects.get', return_value=city_instance)

        mock_filter = mocker.patch('city.models.City.objects.filter')
        mock_count = mock_filter.return_value.count
        mock_count.return_value = 0

        result = repo.get_number_of_cities_in_region_by_city(city_id=123)

        assert result == 0


# =============================================================================
# Тесты для get_rank_in_country_by_visits
# =============================================================================


class TestGetRankInCountryByVisits:
    """Тесты для метода get_rank_in_country_by_visits."""

    def test_returns_rank_when_found(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет корректный возврат ранга города."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [
            {'id': 1, 'title': 'A', 'visits': 100, 'rank': 1},
            {'id': 42, 'title': 'B', 'visits': 50, 'rank': 2},
            {'id': 3, 'title': 'C', 'visits': 10, 'rank': 3},
        ]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)

        result = repo.get_rank_in_country_by_visits(city_id=42)

        assert result == 2

    def test_returns_zero_when_not_found(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет возврат 0, если город не найден в рейтинге."""
        mock_city.id = 999
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [{'id': i, 'rank': i} for i in range(1, 10)]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)

        result = repo.get_rank_in_country_by_visits(city_id=999)

        assert result == 0

    def test_returns_zero_when_empty_queryset(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет возврат 0 при пустом списке городов."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = []
        mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)

        result = repo.get_rank_in_country_by_visits(city_id=42)

        assert result == 0

    def test_raises_when_city_not_exists(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет пробрасывание исключения при отсутствии города."""
        mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

        with pytest.raises(City.DoesNotExist):
            repo.get_rank_in_country_by_visits(city_id=999)

    def test_handles_rank_none(self, mocker: Any, repo: CityRepository, mock_city: Mock) -> None:
        """Проверяет обработку rank=None."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [{'id': 42, 'title': 'B', 'visits': 50, 'rank': None}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)

        result = repo.get_rank_in_country_by_visits(city_id=42)

        assert result == 0

    def test_handles_missing_id_key(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет обработку отсутствия ключа 'id' в данных."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [{'rank': 1}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)

        result = repo.get_rank_in_country_by_visits(city_id=42)

        assert result == 0

    def test_handles_missing_rank_key(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет обработку отсутствия ключа 'rank' в данных."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [{'id': 42}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)

        result = repo.get_rank_in_country_by_visits(city_id=42)

        assert result == 0

    def test_handles_non_dict_data(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет обработку некорректных данных (не словарь)."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = ['not a dict', 123]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)

        result = repo.get_rank_in_country_by_visits(city_id=42)

        assert result == 0

    def test_returns_first_when_duplicate_ids(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет возврат ранга первого найденного при дубликатах."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [
            {'id': 42, 'rank': 2},
            {'id': 42, 'rank': 3},
        ]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)

        result = repo.get_rank_in_country_by_visits(city_id=42)

        assert result == 2

    def test_filters_by_country_id(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет, что фильтрация происходит по country_id."""
        mock_city.country.id = 5
        mocker.patch.object(repo, 'get_by_id', return_value=mock_city)

        ranked_data = [{'id': 42, 'title': 'B', 'visits': 50, 'rank': 1}]
        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mock_filter = mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)

        repo.get_rank_in_country_by_visits(city_id=42)

        mock_filter.assert_called_once_with(country_id=5)


# =============================================================================
# Тесты для get_rank_in_country_by_users
# =============================================================================


class TestGetRankInCountryByUsers:
    """Тесты для метода get_rank_in_country_by_users."""

    def test_returns_rank_when_found(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет корректный возврат ранга города."""
        ranked_data = [
            {'id': 1, 'rank': 1},
            {'id': 5, 'rank': 3},
            {'id': 7, 'rank': 2},
        ]
        mock_queryset = mocker.patch('city.models.City.objects.annotate')
        mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data

        result = repo.get_rank_in_country_by_users(city_id=5)

        assert result == 3

    def test_returns_zero_when_not_found(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат 0, если город не найден."""
        ranked_data = [{'id': 1, 'rank': 1}, {'id': 2, 'rank': 2}]
        mock_queryset = mocker.patch('city.models.City.objects.annotate')
        mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data

        result = repo.get_rank_in_country_by_users(city_id=99)

        assert result == 0

    def test_returns_zero_when_empty_data(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат 0 при пустом списке."""
        ranked_data: list[dict[str, Any]] = []
        mock_queryset = mocker.patch('city.models.City.objects.annotate')
        mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data

        result = repo.get_rank_in_country_by_users(city_id=5)

        assert result == 0

    def test_returns_first_rank_when_duplicate_ids(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат первого ранга при дубликатах."""
        ranked_data = [{'id': 5, 'rank': 2}, {'id': 5, 'rank': 3}]
        mock_queryset = mocker.patch('city.models.City.objects.annotate')
        mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data

        result = repo.get_rank_in_country_by_users(city_id=5)

        assert result == 2

    def test_returns_none_when_rank_is_none(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат None при rank=None."""
        ranked_data = [{'id': 5, 'rank': None}]
        mock_queryset = mocker.patch('city.models.City.objects.annotate')
        mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data

        result = repo.get_rank_in_country_by_users(city_id=5)

        assert result is None

    def test_raises_key_error_when_id_missing(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет выбрасывание KeyError при отсутствии 'id'."""
        ranked_data = [{'rank': 1}]
        mock_queryset = mocker.patch('city.models.City.objects.annotate')
        mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data

        with pytest.raises(KeyError):
            repo.get_rank_in_country_by_users(city_id=5)

    def test_raises_key_error_when_rank_missing(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет выбрасывание KeyError при отсутствии 'rank'."""
        ranked_data = [{'id': 5}]
        mock_queryset = mocker.patch('city.models.City.objects.annotate')
        mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data

        with pytest.raises(KeyError):
            repo.get_rank_in_country_by_users(city_id=5)

    def test_raises_type_error_when_non_dict(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет выбрасывание TypeError при некорректных данных."""
        ranked_data = ['not a dict', 123]
        mock_queryset = mocker.patch('city.models.City.objects.annotate')
        mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data

        with pytest.raises(TypeError):
            repo.get_rank_in_country_by_users(city_id=5)


# =============================================================================
# Тесты для get_rank_in_region_by_visits
# =============================================================================


class TestGetRankInRegionByVisits:
    """Тесты для метода get_rank_in_region_by_visits."""

    def test_returns_rank_when_city_has_region(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет корректный возврат ранга для города с регионом."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [
            {'id': 1, 'rank': 1},
            {'id': 42, 'rank': 2},
            {'id': 3, 'rank': 3},
        ]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset

        result = repo.get_rank_in_region_by_visits(city_id=42)

        assert result == 2
        mock_select_related.assert_called_once_with('region')

    def test_returns_rank_when_city_has_no_region(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет использование страны вместо региона, если регион отсутствует."""
        mock_city = Mock(id=42, region=None, country=Mock(id=1))
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [{'id': 42, 'rank': 1}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset

        result = repo.get_rank_in_region_by_visits(city_id=42)

        assert result == 1
        mock_select_related.assert_called_once_with('country')

    def test_returns_zero_when_city_not_found(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат 0 при отсутствии города."""
        mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

        result = repo.get_rank_in_region_by_visits(city_id=999)

        assert result == 0

    def test_returns_zero_when_multiple_cities_returned(
        self, mocker: Any, repo: CityRepository
    ) -> None:
        """Проверяет возврат 0 при дубликатах."""
        mocker.patch('city.models.City.objects.get', side_effect=City.MultipleObjectsReturned)

        result = repo.get_rank_in_region_by_visits(city_id=42)

        assert result == 0

    def test_returns_zero_when_empty_queryset(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет возврат 0 при пустом queryset."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = []
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset

        result = repo.get_rank_in_region_by_visits(city_id=42)

        assert result == 0

    def test_returns_zero_when_city_not_in_ranked_data(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет возврат 0, если города нет в рейтинге."""
        mock_city.id = 99
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [{'id': 1, 'rank': 1}, {'id': 2, 'rank': 2}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset

        result = repo.get_rank_in_region_by_visits(city_id=99)

        assert result == 0


# =============================================================================
# Тесты для get_rank_in_region_by_users
# =============================================================================


class TestGetRankInRegionByUsers:
    """Тесты для метода get_rank_in_region_by_users."""

    def test_returns_rank_when_city_has_region(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет корректный возврат ранга для города с регионом."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [{'id': 42, 'rank': 1}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset

        result = repo.get_rank_in_region_by_users(city_id=42)

        assert result == 1
        mock_select_related.assert_called_once_with('region')

    def test_returns_rank_when_city_has_no_region(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет использование страны вместо региона."""
        mock_city = Mock(id=42, region=None, country=Mock(id=1))
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [{'id': 42, 'rank': 1}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset

        result = repo.get_rank_in_region_by_users(city_id=42)

        assert result == 1
        mock_select_related.assert_called_once_with('country')

    def test_returns_zero_when_city_not_exists(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат 0 при отсутствии города."""
        mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

        result = repo.get_rank_in_region_by_users(city_id=999)

        assert result == 0

    def test_handles_none_rank(self, mocker: Any, repo: CityRepository, mock_city: Mock) -> None:
        """Проверяет обработку rank=None."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [{'id': 42, 'rank': None}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset

        result = repo.get_rank_in_region_by_users(city_id=42)

        assert result is None

    def test_raises_key_error_when_id_missing(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет выбрасывание KeyError при отсутствии 'id'."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [{'rank': 1}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset

        with pytest.raises(KeyError):
            repo.get_rank_in_region_by_users(city_id=42)

    def test_raises_key_error_when_rank_missing(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет выбрасывание KeyError при отсутствии 'rank'."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_data = [{'id': 42}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset

        with pytest.raises(KeyError):
            repo.get_rank_in_region_by_users(city_id=42)


# =============================================================================
# Тесты для _get_cities_near_index
# =============================================================================


class TestGetCitiesNearIndex:
    """Тесты для вспомогательного метода _get_cities_near_index."""

    def test_centered_window(self) -> None:
        """Проверяет центрированное окно из 10 городов."""
        items = [{'id': i} for i in range(1, 21)]
        result = CityRepository._get_cities_near_index(items, 10)

        assert len(result) == 10
        assert result[0]['id'] == 6
        assert result[-1]['id'] == 15

    def test_short_list(self) -> None:
        """Проверяет возврат всего списка, если элементов < 10."""
        items = [{'id': i} for i in range(5)]
        result = CityRepository._get_cities_near_index(items, 2)

        assert result == items
        assert len(result) == 5

    def test_exact_10_items(self) -> None:
        """Проверяет возврат всего списка при ровно 10 элементах."""
        items = [{'id': i} for i in range(10)]
        result = CityRepository._get_cities_near_index(items, 5)

        assert result == items
        assert len(result) == 10

    def test_index_at_start(self) -> None:
        """Проверяет окно в начале списка."""
        items = [{'id': i} for i in range(20)]
        result = CityRepository._get_cities_near_index(items, 0)

        assert result == items[:10]

    def test_index_at_end(self) -> None:
        """Проверяет окно в конце списка."""
        items = [{'id': i} for i in range(20)]
        result = CityRepository._get_cities_near_index(items, 19)

        assert result == items[-10:]

    def test_city_not_in_list(self) -> None:
        """Проверяет возврат [] при отсутствии города в списке."""
        items = [{'id': i} for i in range(20)]
        result = CityRepository._get_cities_near_index(items, 999)

        assert result == []

    def test_empty_list(self) -> None:
        """Проверяет обработку пустого списка."""
        items: list[dict[str, int]] = []
        result = CityRepository._get_cities_near_index(items, 0)

        assert result == []

    def test_one_element(self) -> None:
        """Проверяет список с одним элементом."""
        items = [{'id': 0}]
        result = CityRepository._get_cities_near_index(items, 0)

        assert result == items

    def test_11_elements_middle(self) -> None:
        """Проверяет окно при 11 элементах."""
        items = [{'id': i} for i in range(11)]
        result = CityRepository._get_cities_near_index(items, 5)

        assert len(result) == 10
        assert result == items[1:11]


# =============================================================================
# Тесты для get_neighboring_cities_by_rank_in_country_by_visits
# =============================================================================


class TestGetNeighboringCitiesByRankInCountryByVisits:
    """Тесты для метода get_neighboring_cities_by_rank_in_country_by_visits."""

    def test_returns_neighboring_cities(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет корректный возврат соседних городов."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_cities = [
            {'id': i, 'title': f'City {i}', 'visits': 10 - i, 'rank': i} for i in range(1, 21)
        ]

        mock_all = mocker.patch('city.models.City.objects.all')
        mock_filter = mock_all.return_value.filter
        mock_filter.return_value.annotate.return_value.values.return_value.order_by.return_value = (
            ranked_cities
        )
        mocker.patch.object(repo, '_get_cities_near_index', return_value=ranked_cities[5:15])

        result = repo.get_neighboring_cities_by_rank_in_country_by_visits(city_id=42)

        assert result == ranked_cities[5:15]  # type: ignore[comparison-overlap]

    def test_returns_empty_when_city_not_exists(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат [] при отсутствии города."""
        mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

        result = repo.get_neighboring_cities_by_rank_in_country_by_visits(city_id=999)

        assert result == []

    def test_returns_empty_when_multiple_objects(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат [] при дубликатах."""
        mocker.patch('city.models.City.objects.get', side_effect=City.MultipleObjectsReturned)

        result = repo.get_neighboring_cities_by_rank_in_country_by_visits(city_id=42)

        assert result == []

    def test_filters_by_country(self, mocker: Any, repo: CityRepository, mock_city: Mock) -> None:
        """Проверяет фильтрацию по стране."""
        mock_city.country.id = 5
        mocker.patch('city.models.City.objects.get', return_value=mock_city)

        ranked_cities = [{'id': 42, 'rank': 1}]
        mock_all = mocker.patch('city.models.City.objects.all')
        mock_filter = mock_all.return_value.filter
        mock_filter.return_value.annotate.return_value.values.return_value.order_by.return_value = (
            ranked_cities
        )
        mocker.patch.object(repo, '_get_cities_near_index', return_value=[])

        repo.get_neighboring_cities_by_rank_in_country_by_visits(city_id=42)

        # Проверяем, что filter был вызван с правильным country_id
        mock_filter.assert_called_once_with(country_id=5)


# =============================================================================
# Тесты для get_neighboring_cities_by_rank_in_country_by_users
# =============================================================================


class TestGetNeighboringCitiesByRankInCountryByUsers:
    """Тесты для метода get_neighboring_cities_by_rank_in_country_by_users."""

    def test_returns_neighboring_cities(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет корректный возврат соседних городов."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_cities = [
            {'id': i, 'title': f'City {i}', 'visits': 10 - i, 'rank': i} for i in range(1, 21)
        ]

        mock_filter = mocker.patch('city.models.City.objects.filter')
        mock_filter.return_value.annotate.return_value.values.return_value.order_by.return_value = (
            ranked_cities
        )
        mocker.patch.object(repo, '_get_cities_near_index', return_value=ranked_cities[5:15])

        result = repo.get_neighboring_cities_by_rank_in_country_by_users(city_id=42)

        assert result == ranked_cities[5:15]  # type: ignore[comparison-overlap]
        mock_filter.assert_called_once_with(country_id=1)

    def test_returns_empty_when_city_not_exists(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат [] при отсутствии города."""
        mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

        result = repo.get_neighboring_cities_by_rank_in_country_by_users(city_id=999)

        assert result == []

    def test_returns_empty_when_multiple_objects(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат [] при дубликатах."""
        mocker.patch('city.models.City.objects.get', side_effect=City.MultipleObjectsReturned)

        result = repo.get_neighboring_cities_by_rank_in_country_by_users(city_id=42)

        assert result == []

    def test_returns_empty_when_empty_ranked_list(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет возврат [] при пустом списке."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_cities: list[dict[str, Any]] = []

        mock_filter = mocker.patch('city.models.City.objects.filter')
        mock_filter.return_value.annotate.return_value.values.return_value.order_by.return_value = (
            ranked_cities
        )
        mocker.patch.object(repo, '_get_cities_near_index', return_value=[])

        result = repo.get_neighboring_cities_by_rank_in_country_by_users(city_id=42)

        assert result == []


# =============================================================================
# Тесты для get_neighboring_cities_by_rank_in_region_by_visits
# =============================================================================


class TestGetNeighboringCitiesByRankInRegionByVisits:
    """Тесты для метода get_neighboring_cities_by_rank_in_region_by_visits."""

    def test_returns_cities_for_region(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет возврат городов по региону."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_cities = [
            {'id': i, 'title': f'City {i}', 'visits': 10 - i, 'rank': i} for i in range(1, 21)
        ]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = (
            ranked_cities
        )
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset
        mocker.patch.object(repo, '_get_cities_near_index', return_value=ranked_cities[5:15])

        result = repo.get_neighboring_cities_by_rank_in_region_by_visits(city_id=42)

        assert result == ranked_cities[5:15]  # type: ignore[comparison-overlap]
        mock_select_related.assert_called_once_with('region')
        mock_select_related.return_value.filter.assert_called_once_with(region_id=7)

    def test_returns_cities_for_country_when_no_region(
        self, mocker: Any, repo: CityRepository
    ) -> None:
        """Проверяет использование страны при отсутствии региона."""
        mock_city = Mock(id=42, region=None, country=Mock(id=1))
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_cities = [{'id': 42, 'rank': 1}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = (
            ranked_cities
        )
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset
        mocker.patch.object(repo, '_get_cities_near_index', return_value=ranked_cities)

        result = repo.get_neighboring_cities_by_rank_in_region_by_visits(city_id=42)

        assert result == ranked_cities  # type: ignore[comparison-overlap]
        mock_select_related.assert_called_once_with('country')
        mock_select_related.return_value.filter.assert_called_once_with(country_id=1)

    def test_returns_empty_when_city_not_exists(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат [] при отсутствии города."""
        mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

        result = repo.get_neighboring_cities_by_rank_in_region_by_visits(city_id=999)

        assert result == []

    def test_returns_empty_when_multiple_objects(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат [] при дубликатах."""
        mocker.patch('city.models.City.objects.get', side_effect=City.MultipleObjectsReturned)

        result = repo.get_neighboring_cities_by_rank_in_region_by_visits(city_id=42)

        assert result == []


# =============================================================================
# Тесты для get_neighboring_cities_by_rank_in_region_by_users
# =============================================================================


class TestGetNeighboringCitiesByRankInRegionByUsers:
    """Тесты для метода get_neighboring_cities_by_rank_in_region_by_users."""

    def test_returns_cities_for_region(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет возврат городов по региону."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_cities = [
            {'id': i, 'title': f'City {i}', 'visits': 10 - i, 'rank': i} for i in range(1, 21)
        ]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = (
            ranked_cities
        )
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset
        mocker.patch.object(repo, '_get_cities_near_index', return_value=ranked_cities[5:15])

        result = repo.get_neighboring_cities_by_rank_in_region_by_users(city_id=42)

        assert result == ranked_cities[5:15]  # type: ignore[comparison-overlap]
        mock_select_related.assert_called_once_with('region')
        mock_select_related.return_value.filter.assert_called_once_with(region_id=7)

    def test_returns_cities_for_country_when_no_region(
        self, mocker: Any, repo: CityRepository
    ) -> None:
        """Проверяет использование страны при отсутствии региона."""
        mock_city = Mock(id=42, region=None, country=Mock(id=1))
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_cities = [{'id': 42, 'rank': 1}]

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = (
            ranked_cities
        )
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset
        mocker.patch.object(repo, '_get_cities_near_index', return_value=ranked_cities)

        result = repo.get_neighboring_cities_by_rank_in_region_by_users(city_id=42)

        assert result == ranked_cities  # type: ignore[comparison-overlap]
        mock_select_related.assert_called_once_with('country')
        mock_select_related.return_value.filter.assert_called_once_with(country_id=1)

    def test_returns_empty_when_city_not_exists(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат [] при отсутствии города."""
        mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

        result = repo.get_neighboring_cities_by_rank_in_region_by_users(city_id=999)

        assert result == []

    def test_returns_empty_when_multiple_objects(self, mocker: Any, repo: CityRepository) -> None:
        """Проверяет возврат [] при дубликатах."""
        mocker.patch('city.models.City.objects.get', side_effect=City.MultipleObjectsReturned)

        result = repo.get_neighboring_cities_by_rank_in_region_by_users(city_id=42)

        assert result == []

    def test_returns_empty_when_empty_ranked_list(
        self, mocker: Any, repo: CityRepository, mock_city: Mock
    ) -> None:
        """Проверяет возврат [] при пустом списке городов."""
        mocker.patch('city.models.City.objects.get', return_value=mock_city)
        ranked_cities: list[dict[str, Any]] = []

        mock_queryset = mocker.Mock()
        mock_queryset.annotate.return_value.values.return_value.order_by.return_value = (
            ranked_cities
        )
        mock_select_related = mocker.patch('city.models.City.objects.select_related')
        mock_select_related.return_value.filter.return_value = mock_queryset
        mocker.patch.object(repo, '_get_cities_near_index', return_value=[])

        result = repo.get_neighboring_cities_by_rank_in_region_by_users(city_id=42)

        assert result == []
