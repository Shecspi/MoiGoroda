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


@pytest.fixture(autouse=True)
def mock_helpers(mocker):
    mocker.patch(
        'city.services.visited_city_service.get_number_of_users_who_visit_city', return_value=5
    )
    mocker.patch('city.services.visited_city_service.get_total_number_of_visits', return_value=100)
    mocker.patch('city.services.visited_city_service.get_number_of_cities', return_value=50)
    mocker.patch(
        'city.services.visited_city_service.get_number_of_cities_in_region_by_city', return_value=10
    )
    mocker.patch('city.services.visited_city_service.get_rank_by_visits_of_city', return_value=1)
    mocker.patch('city.services.visited_city_service.get_rank_by_users_of_city', return_value=2)
    mocker.patch(
        'city.services.visited_city_service.get_rank_by_visits_of_city_in_region', return_value=3
    )
    mocker.patch(
        'city.services.visited_city_service.get_rank_by_users_of_city_in_region', return_value=4
    )
    mocker.patch(
        'city.services.visited_city_service.get_neighboring_cities_by_users_rank', return_value=[]
    )
    mocker.patch(
        'city.services.visited_city_service.get_neighboring_cities_by_visits_rank', return_value=[]
    )
    mocker.patch(
        'city.services.visited_city_service.get_neighboring_cities_in_region_by_users_rank',
        return_value=[],
    )
    mocker.patch(
        'city.services.visited_city_service.get_neighboring_cities_in_region_by_visits_rank',
        return_value=[],
    )


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
    visited_city_repo.count_user_visits.assert_called_once_with(fake_city, fake_user)
    visited_city_repo.count_all_visits.assert_called_once_with(fake_city)
    visited_city_repo.get_user_visits.assert_called_once_with(fake_city, fake_user)


def test_helpers_raise_exception(
    city_repo,
    visited_city_repo,
    fake_user,
    fake_request,
    fake_city,
    mock_collections,
    mock_logger,
    mocker,
):
    # Пусть одна из вспомогательных функций выбрасывает исключение
    mocker.patch(
        'city.services.visited_city_service.get_number_of_users_who_visit_city',
        side_effect=Exception('Helper failure'),
    )

    service = VisitedCityService(city_repo, visited_city_repo, fake_request)

    # Проверяем, что исключение пробрасывается (т.к. в коде нет try/except для этих вызовов)
    with pytest.raises(Exception) as excinfo:
        service.get_city_details(city_id=1, user=fake_user)

    assert 'Helper failure' in str(excinfo.value)


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
