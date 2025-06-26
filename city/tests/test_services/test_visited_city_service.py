import pytest
from django.http import Http404
from city.dto import CityDetailsDTO
from city.models import City
from city.services.visited_city_service import VisitedCityService


@pytest.fixture
def fake_city(mocker):
    return mocker.Mock(spec=City)


@pytest.fixture
def fake_user(mocker):
    user = mocker.Mock()
    user.is_authenticated = True
    return user


@pytest.fixture
def fake_request(mocker):
    return mocker.Mock()


@pytest.fixture
def city_repo(mocker, fake_city):
    repo = mocker.Mock()
    repo.get_by_id.return_value = fake_city
    return repo


@pytest.fixture
def visited_city_repo(mocker):
    repo = mocker.Mock()
    repo.get_average_rating.return_value = 4.5
    repo.get_popular_months.return_value = [6, 7, 8]
    repo.count_user_visits.return_value = 2
    repo.count_all_visits.return_value = 10
    repo.get_user_visits.return_value = [
        {
            'id': 1,
            'date_of_visit': '2024-06-01',
            'rating': 5,
            'impression': 'Great!',
            'city__title': 'TestCity',
        }
    ]
    return repo


@pytest.fixture
def mock_collections(mocker):
    return mocker.patch(
        'city.services.visited_city_service.Collection.objects.filter',
        return_value=['collection1', 'collection2'],
    )


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch('city.services.visited_city_service.logger')


def test_get_city_details_success(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
):
    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    result = service.get_city_details(city_id=1, user=fake_user)

    assert isinstance(result, CityDetailsDTO)
    assert result.city == fake_city
    assert result.average_rating == 4.5
    assert result.popular_months == ['Июнь', 'Июль', 'Август']
    assert result.visits == visited_city_repo.get_user_visits.return_value
    assert result.collections == ['collection1', 'collection2']
    assert result.number_of_visits == 2
    assert result.number_of_visits_all_users == 10
    mock_logger.info.assert_called_once()


def test_get_city_details_city_does_not_exist(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    mock_logger,
):
    city_repo.get_by_id.side_effect = City.DoesNotExist

    service = VisitedCityService(city_repo, visited_city_repo, fake_request)

    with pytest.raises(Http404):
        service.get_city_details(city_id=999, user=fake_user)

    mock_logger.warning.assert_called_once()


def test_get_city_details_unauthenticated_user(
    city_repo,
    visited_city_repo,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
    mocker,
):
    user = mocker.Mock()
    user.is_authenticated = False

    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    result = service.get_city_details(city_id=1, user=user)

    assert result.number_of_visits == 0
    assert result.visits == []


def test_get_city_details_popular_months_sorting(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
):
    # Проверим, что популярные месяцы сортируются правильно, даже если приходят неупорядоченно
    visited_city_repo.get_popular_months.return_value = [
        8,
        6,
        7,
    ]  # Август, Июнь, Июль (в непоследовательном порядке)

    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    result = service.get_city_details(city_id=1, user=fake_user)

    # Месяцы должны быть отсортированы в соответствии с MONTH_NAMES
    assert result.popular_months == ['Июнь', 'Июль', 'Август']


def test_get_city_details_empty_popular_months(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
):
    # Проверка пустого списка популярных месяцев
    visited_city_repo.get_popular_months.return_value = []

    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    result = service.get_city_details(city_id=1, user=fake_user)

    assert result.popular_months == []


def test_get_city_details_average_rating_none(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
):
    # Проверка, если средний рейтинг None
    visited_city_repo.get_average_rating.return_value = None

    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    result = service.get_city_details(city_id=1, user=fake_user)

    assert result.average_rating is None


def test_logger_called_with_correct_message(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
):
    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    service.get_city_details(city_id=1, user=fake_user)

    # Проверяем, что info лог содержит нужную информацию
    mock_logger.info.assert_called_once()
    args, kwargs = mock_logger.info.call_args
    assert 'Viewing the visited city #1' in args[1]


def test_logger_warning_called_with_correct_message_on_city_not_found(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    mock_logger,
):
    city_repo.get_by_id.side_effect = City.DoesNotExist

    service = VisitedCityService(city_repo, visited_city_repo, fake_request)

    with pytest.raises(Http404):
        service.get_city_details(city_id=999, user=fake_user)

    mock_logger.warning.assert_called_once()
    args, kwargs = mock_logger.warning.call_args
    assert 'Attempt to access a non-existent city #999' in args[1]


def test_repo_methods_called_with_correct_args(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
):
    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    service.get_city_details(city_id=1, user=fake_user)

    city_repo.get_by_id.assert_called_once_with(1)
    visited_city_repo.get_average_rating.assert_called_once_with(fake_city)
    visited_city_repo.get_popular_months.assert_called_once_with(fake_city)
    visited_city_repo.count_user_visits.assert_called_once_with(1, fake_user)
    visited_city_repo.count_all_visits.assert_called_once_with(1)
    visited_city_repo.get_user_visits.assert_called_once_with(1, fake_user)


def test_unauthenticated_user_no_calls_to_user_specific_methods(
    city_repo,
    visited_city_repo,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
    mocker,
):
    user = mocker.Mock()
    user.is_authenticated = False

    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    result = service.get_city_details(city_id=1, user=user)

    assert result.number_of_visits == 0
    assert result.visits == []

    # Проверяем, что методы, которые требуют user, не вызываются
    visited_city_repo.count_user_visits.assert_not_called()
    visited_city_repo.get_user_visits.assert_not_called()


def test_get_city_details_empty_collections(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    fake_city,
    mocker,
    mock_logger,
):
    mocker.patch('city.services.visited_city_service.Collection.objects.filter', return_value=[])
    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    result = service.get_city_details(city_id=1, user=fake_user)
    assert result.collections == []


def test_get_city_details_empty_visits(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
):
    visited_city_repo.get_user_visits.return_value = []
    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    result = service.get_city_details(city_id=1, user=fake_user)
    assert result.visits == []


def test_get_city_details_all_dto_fields(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
):
    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    result = service.get_city_details(city_id=1, user=fake_user)
    # Проверяем, что все основные поля DTO присутствуют и не None (кроме тех, что могут быть пустыми)
    assert hasattr(result, 'city')
    assert hasattr(result, 'average_rating')
    assert hasattr(result, 'popular_months')
    assert hasattr(result, 'visits')
    assert hasattr(result, 'collections')
    assert hasattr(result, 'number_of_visits')
    assert hasattr(result, 'number_of_visits_all_users')
    assert hasattr(result, 'number_of_users_who_visit_city')
    assert hasattr(result, 'number_of_cities_in_country')
    assert hasattr(result, 'number_of_cities_in_region')
    assert hasattr(result, 'rank_in_country_by_visits')
    assert hasattr(result, 'rank_in_country_by_users')
    assert hasattr(result, 'rank_in_region_by_visits')
    assert hasattr(result, 'rank_in_region_by_users')
    assert hasattr(result, 'neighboring_cities_by_rank_in_region_by_users')
    assert hasattr(result, 'neighboring_cities_by_rank_in_region_by_visits')
    assert hasattr(result, 'neighboring_cities_by_rank_in_country_by_visits')
    assert hasattr(result, 'neighboring_cities_by_rank_in_country_by_users')


def test_get_city_details_repo_exception(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
):
    visited_city_repo.count_user_visits.side_effect = Exception('DB error')
    service = VisitedCityService(city_repo, visited_city_repo, fake_request)
    with pytest.raises(Exception) as excinfo:
        service.get_city_details(city_id=1, user=fake_user)
    assert 'DB error' in str(excinfo.value)
