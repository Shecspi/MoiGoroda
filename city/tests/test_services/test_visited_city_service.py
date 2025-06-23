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
