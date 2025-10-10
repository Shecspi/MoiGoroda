"""
Unit тесты для VisitedCityService (city/services/visited_city_service.py).

Проверяется:
- Получение деталей города
- Обработка ошибок (Http404)
- Формирование DTO
- Работа с аутентифицированными и неаутентифицированными пользователями
- Логирование
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from django.http import Http404

from city.dto import CityDetailsDTO
from city.models import City
from city.services.visited_city_service import VisitedCityService


@pytest.mark.unit
class TestVisitedCityServiceInit:
    """Тесты инициализации сервиса."""

    def test_service_initialization(self) -> None:
        """Сервис корректно инициализируется."""
        mock_city_repo = Mock()
        mock_vc_repo = Mock()
        mock_request = Mock()

        service = VisitedCityService(mock_city_repo, mock_vc_repo, mock_request)

        assert service.city_repo == mock_city_repo
        assert service.visited_city_repo == mock_vc_repo
        assert service.request == mock_request


@pytest.mark.unit
class TestVisitedCityServiceGetCityDetails:
    """Тесты метода get_city_details."""

    @patch('city.services.visited_city_service.logger')
    @patch('city.services.visited_city_service.Collection.objects')
    def test_get_city_details_city_not_exists_raises_404(
        self, mock_collection: MagicMock, mock_logger: MagicMock
    ) -> None:
        """При отсутствии города выбрасывается Http404."""
        mock_city_repo = Mock()
        mock_city_repo.get_by_id.side_effect = City.DoesNotExist
        mock_vc_repo = Mock()
        mock_request = Mock()
        mock_user = Mock()

        service = VisitedCityService(mock_city_repo, mock_vc_repo, mock_request)

        with pytest.raises(Http404):
            service.get_city_details(city_id=999, user=mock_user)

        # Проверяем что было залогировано предупреждение
        mock_logger.warning.assert_called_once()
        assert '999' in str(mock_logger.warning.call_args)

    @patch('city.services.visited_city_service.logger')
    @patch('city.services.visited_city_service.Collection.objects')
    def test_get_city_details_returns_dto(
        self, mock_collection: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Метод возвращает CityDetailsDTO."""
        # Настройка моков
        mock_city = Mock()
        mock_city.country = Mock(id=1, code='RU')

        mock_city_repo = Mock()
        mock_city_repo.get_by_id.return_value = mock_city
        mock_city_repo.get_number_of_cities.return_value = 100
        mock_city_repo.get_number_of_cities_in_region_by_city.return_value = 50
        mock_city_repo.get_rank_in_country_by_visits.return_value = 10
        mock_city_repo.get_rank_in_country_by_users.return_value = 15
        mock_city_repo.get_rank_in_region_by_visits.return_value = 5
        mock_city_repo.get_rank_in_region_by_users.return_value = 7
        mock_city_repo.get_neighboring_cities_by_rank_in_region_by_users.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_region_by_visits.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_country_by_users.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_country_by_visits.return_value = []

        mock_vc_repo = Mock()
        mock_vc_repo.get_average_rating.return_value = 4.5
        mock_vc_repo.get_popular_months.return_value = [1, 5, 12]
        mock_vc_repo.get_user_visits.return_value = []
        mock_vc_repo.count_user_visits.return_value = 0
        mock_vc_repo.count_all_visits.return_value = 100
        mock_vc_repo.get_number_of_users_who_visit_city.return_value = 50

        mock_collection.filter.return_value = []

        mock_request = Mock()
        mock_user = Mock(is_authenticated=True)

        service = VisitedCityService(mock_city_repo, mock_vc_repo, mock_request)

        result = service.get_city_details(city_id=1, user=mock_user)

        assert isinstance(result, CityDetailsDTO)
        assert result.city == mock_city
        assert result.average_rating == 4.5
        assert result.number_of_cities_in_country == 100

    @patch('city.services.visited_city_service.logger')
    @patch('city.services.visited_city_service.Collection.objects')
    def test_get_city_details_logs_info(
        self, mock_collection: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Метод логирует просмотр города."""
        mock_city = Mock()
        mock_city.country = Mock(id=1, code='RU')

        mock_city_repo = Mock()
        mock_city_repo.get_by_id.return_value = mock_city
        mock_city_repo.get_number_of_cities.return_value = 100
        mock_city_repo.get_number_of_cities_in_region_by_city.return_value = 50
        mock_city_repo.get_rank_in_country_by_visits.return_value = 10
        mock_city_repo.get_rank_in_country_by_users.return_value = 15
        mock_city_repo.get_rank_in_region_by_visits.return_value = 5
        mock_city_repo.get_rank_in_region_by_users.return_value = 7
        mock_city_repo.get_neighboring_cities_by_rank_in_region_by_users.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_region_by_visits.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_country_by_users.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_country_by_visits.return_value = []

        mock_vc_repo = Mock()
        mock_vc_repo.get_average_rating.return_value = 0
        mock_vc_repo.get_popular_months.return_value = []
        mock_vc_repo.get_user_visits.return_value = []
        mock_vc_repo.count_user_visits.return_value = 0
        mock_vc_repo.count_all_visits.return_value = 0
        mock_vc_repo.get_number_of_users_who_visit_city.return_value = 0

        mock_collection.filter.return_value = []

        mock_request = Mock()
        mock_user = Mock(is_authenticated=False)

        service = VisitedCityService(mock_city_repo, mock_vc_repo, mock_request)
        service.get_city_details(city_id=42, user=mock_user)

        # Проверяем логирование
        mock_logger.info.assert_called_once()
        assert '42' in str(mock_logger.info.call_args)

    @patch('city.services.visited_city_service.logger')
    @patch('city.services.visited_city_service.Collection.objects')
    def test_get_city_details_for_unauthenticated_user(
        self, mock_collection: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Для неаутентифицированного пользователя не запрашиваются его визиты."""
        mock_city = Mock()
        mock_city.country = Mock(id=1, code='RU')

        mock_city_repo = Mock()
        mock_city_repo.get_by_id.return_value = mock_city
        mock_city_repo.get_number_of_cities.return_value = 100
        mock_city_repo.get_number_of_cities_in_region_by_city.return_value = 50
        mock_city_repo.get_rank_in_country_by_visits.return_value = 10
        mock_city_repo.get_rank_in_country_by_users.return_value = 15
        mock_city_repo.get_rank_in_region_by_visits.return_value = 5
        mock_city_repo.get_rank_in_region_by_users.return_value = 7
        mock_city_repo.get_neighboring_cities_by_rank_in_region_by_users.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_region_by_visits.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_country_by_users.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_country_by_visits.return_value = []

        mock_vc_repo = Mock()
        mock_vc_repo.get_average_rating.return_value = 0
        mock_vc_repo.get_popular_months.return_value = []

        mock_collection.filter.return_value = []

        mock_request = Mock()
        mock_user = Mock(is_authenticated=False)

        service = VisitedCityService(mock_city_repo, mock_vc_repo, mock_request)
        result = service.get_city_details(city_id=1, user=mock_user)

        # Для неаутентифицированного пользователя не должны вызываться
        mock_vc_repo.get_user_visits.assert_not_called()
        mock_vc_repo.count_user_visits.assert_not_called()

        # Проверяем что вернулись пустые значения
        assert result.visits == []
        assert result.number_of_visits == 0

    @patch('city.services.visited_city_service.logger')
    @patch('city.services.visited_city_service.Collection.objects')
    def test_get_city_details_for_authenticated_user(
        self, mock_collection: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Для аутентифицированного пользователя запрашиваются его визиты."""
        mock_city = Mock()
        mock_city.country = Mock(id=1, code='RU')

        mock_city_repo = Mock()
        mock_city_repo.get_by_id.return_value = mock_city
        mock_city_repo.get_number_of_cities.return_value = 100
        mock_city_repo.get_number_of_cities_in_region_by_city.return_value = 50
        mock_city_repo.get_rank_in_country_by_visits.return_value = 10
        mock_city_repo.get_rank_in_country_by_users.return_value = 15
        mock_city_repo.get_rank_in_region_by_visits.return_value = 5
        mock_city_repo.get_rank_in_region_by_users.return_value = 7
        mock_city_repo.get_neighboring_cities_by_rank_in_region_by_users.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_region_by_visits.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_country_by_users.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_country_by_visits.return_value = []

        mock_visits = [Mock(), Mock()]
        mock_vc_repo = Mock()
        mock_vc_repo.get_average_rating.return_value = 4.5
        mock_vc_repo.get_popular_months.return_value = [5]
        mock_vc_repo.get_user_visits.return_value = mock_visits
        mock_vc_repo.count_user_visits.return_value = 2
        mock_vc_repo.count_all_visits.return_value = 100
        mock_vc_repo.get_number_of_users_who_visit_city.return_value = 50

        mock_collection.filter.return_value = []

        mock_request = Mock()
        mock_user = Mock(is_authenticated=True)

        service = VisitedCityService(mock_city_repo, mock_vc_repo, mock_request)
        result = service.get_city_details(city_id=1, user=mock_user)

        # Для аутентифицированного пользователя должны вызываться
        mock_vc_repo.get_user_visits.assert_called_once_with(1, mock_user)
        mock_vc_repo.count_user_visits.assert_called_once_with(1, mock_user)

        # Проверяем возвращённые данные
        assert result.visits == mock_visits
        assert result.number_of_visits == 2


@pytest.mark.unit
class TestVisitedCityServicePopularMonths:
    """Тесты обработки популярных месяцев."""

    @patch('city.services.visited_city_service.logger')
    @patch('city.services.visited_city_service.Collection.objects')
    def test_popular_months_sorted_and_named(
        self, mock_collection: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Популярные месяцы сортируются и переводятся в названия."""
        mock_city = Mock()
        mock_city.country = Mock(id=1, code='RU')

        mock_city_repo = self._create_mock_city_repo(mock_city)

        # Возвращаем месяцы в неправильном порядке: 12, 1, 5
        mock_vc_repo = Mock()
        mock_vc_repo.get_average_rating.return_value = 0
        mock_vc_repo.get_popular_months.return_value = [12, 1, 5]
        mock_vc_repo.get_user_visits.return_value = []
        mock_vc_repo.count_user_visits.return_value = 0
        mock_vc_repo.count_all_visits.return_value = 0
        mock_vc_repo.get_number_of_users_who_visit_city.return_value = 0

        mock_collection.filter.return_value = []

        mock_request = Mock()
        mock_user = Mock(is_authenticated=False)

        service = VisitedCityService(mock_city_repo, mock_vc_repo, mock_request)
        result = service.get_city_details(city_id=1, user=mock_user)

        # Проверяем что месяцы отсортированы в правильном порядке
        assert result.popular_months == ['Январь', 'Май', 'Декабрь']

    @patch('city.services.visited_city_service.logger')
    @patch('city.services.visited_city_service.Collection.objects')
    def test_popular_months_empty(self, mock_collection: MagicMock, mock_logger: MagicMock) -> None:
        """Пустой список популярных месяцев."""
        mock_city = Mock()
        mock_city.country = Mock(id=1, code='RU')

        mock_city_repo = self._create_mock_city_repo(mock_city)

        mock_vc_repo = Mock()
        mock_vc_repo.get_average_rating.return_value = 0
        mock_vc_repo.get_popular_months.return_value = []
        mock_vc_repo.get_user_visits.return_value = []
        mock_vc_repo.count_user_visits.return_value = 0
        mock_vc_repo.count_all_visits.return_value = 0
        mock_vc_repo.get_number_of_users_who_visit_city.return_value = 0

        mock_collection.filter.return_value = []

        mock_request = Mock()
        mock_user = Mock(is_authenticated=False)

        service = VisitedCityService(mock_city_repo, mock_vc_repo, mock_request)
        result = service.get_city_details(city_id=1, user=mock_user)

        assert result.popular_months == []

    @patch('city.services.visited_city_service.logger')
    @patch('city.services.visited_city_service.Collection.objects')
    def test_popular_months_removes_duplicates(
        self, mock_collection: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Дубликаты месяцев удаляются."""
        mock_city = Mock()
        mock_city.country = Mock(id=1, code='RU')

        mock_city_repo = self._create_mock_city_repo(mock_city)

        # Возвращаем дубликаты
        mock_vc_repo = Mock()
        mock_vc_repo.get_average_rating.return_value = 0
        mock_vc_repo.get_popular_months.return_value = [5, 5, 5, 12, 12]
        mock_vc_repo.get_user_visits.return_value = []
        mock_vc_repo.count_user_visits.return_value = 0
        mock_vc_repo.count_all_visits.return_value = 0
        mock_vc_repo.get_number_of_users_who_visit_city.return_value = 0

        mock_collection.filter.return_value = []

        mock_request = Mock()
        mock_user = Mock(is_authenticated=False)

        service = VisitedCityService(mock_city_repo, mock_vc_repo, mock_request)
        result = service.get_city_details(city_id=1, user=mock_user)

        # Должно быть только 2 уникальных месяца
        assert len(result.popular_months) == 2
        assert result.popular_months == ['Май', 'Декабрь']

    def _create_mock_city_repo(self, mock_city: Mock) -> Mock:
        """Вспомогательный метод для создания мока city_repo."""
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = mock_city
        mock_repo.get_number_of_cities.return_value = 0
        mock_repo.get_number_of_cities_in_region_by_city.return_value = 0
        mock_repo.get_rank_in_country_by_visits.return_value = 0
        mock_repo.get_rank_in_country_by_users.return_value = 0
        mock_repo.get_rank_in_region_by_visits.return_value = 0
        mock_repo.get_rank_in_region_by_users.return_value = 0
        mock_repo.get_neighboring_cities_by_rank_in_region_by_users.return_value = []
        mock_repo.get_neighboring_cities_by_rank_in_region_by_visits.return_value = []
        mock_repo.get_neighboring_cities_by_rank_in_country_by_users.return_value = []
        mock_repo.get_neighboring_cities_by_rank_in_country_by_visits.return_value = []
        return mock_repo


@pytest.mark.unit
class TestVisitedCityServiceCollections:
    """Тесты работы с коллекциями."""

    @patch('city.services.visited_city_service.logger')
    @patch('city.services.visited_city_service.Collection.objects')
    def test_collections_filtered_by_city(
        self, mock_collection: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Коллекции фильтруются по городу."""
        mock_city = Mock()
        mock_city.country = Mock(id=1, code='RU')

        mock_city_repo = Mock()
        mock_city_repo.get_by_id.return_value = mock_city
        mock_city_repo.get_number_of_cities.return_value = 0
        mock_city_repo.get_number_of_cities_in_region_by_city.return_value = 0
        mock_city_repo.get_rank_in_country_by_visits.return_value = 0
        mock_city_repo.get_rank_in_country_by_users.return_value = 0
        mock_city_repo.get_rank_in_region_by_visits.return_value = 0
        mock_city_repo.get_rank_in_region_by_users.return_value = 0
        mock_city_repo.get_neighboring_cities_by_rank_in_region_by_users.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_region_by_visits.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_country_by_users.return_value = []
        mock_city_repo.get_neighboring_cities_by_rank_in_country_by_visits.return_value = []

        mock_vc_repo = Mock()
        mock_vc_repo.get_average_rating.return_value = 0
        mock_vc_repo.get_popular_months.return_value = []
        mock_vc_repo.get_user_visits.return_value = []
        mock_vc_repo.count_user_visits.return_value = 0
        mock_vc_repo.count_all_visits.return_value = 0
        mock_vc_repo.get_number_of_users_who_visit_city.return_value = 0

        mock_collections = [Mock(), Mock()]
        mock_collection.filter.return_value = mock_collections

        mock_request = Mock()
        mock_user = Mock(is_authenticated=False)

        service = VisitedCityService(mock_city_repo, mock_vc_repo, mock_request)
        result = service.get_city_details(city_id=1, user=mock_user)

        # Проверяем что коллекции были отфильтрованы по city
        mock_collection.filter.assert_called_once_with(city=mock_city)
        assert len(result.collections) == 2


@pytest.mark.unit
class TestVisitedCityServiceMonthNames:
    """Тесты константы MONTH_NAMES."""

    def test_month_names_has_13_elements(self) -> None:
        """MONTH_NAMES содержит 13 элементов (0-индекс пустой)."""
        assert len(VisitedCityService.MONTH_NAMES) == 13

    def test_month_names_first_element_empty(self) -> None:
        """Первый элемент (индекс 0) пустой."""
        assert VisitedCityService.MONTH_NAMES[0] == ''

    def test_month_names_january_at_index_1(self) -> None:
        """Январь находится по индексу 1."""
        assert VisitedCityService.MONTH_NAMES[1] == 'Январь'

    def test_month_names_december_at_index_12(self) -> None:
        """Декабрь находится по индексу 12."""
        assert VisitedCityService.MONTH_NAMES[12] == 'Декабрь'

    def test_month_names_all_months_present(self) -> None:
        """Все месяцы присутствуют."""
        expected_months = [
            '',
            'Январь',
            'Февраль',
            'Март',
            'Апрель',
            'Май',
            'Июнь',
            'Июль',
            'Август',
            'Сентябрь',
            'Октябрь',
            'Ноябрь',
            'Декабрь',
        ]

        assert VisitedCityService.MONTH_NAMES == expected_months
