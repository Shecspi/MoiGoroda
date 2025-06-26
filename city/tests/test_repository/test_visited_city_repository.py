import pytest
from pytest_mock import MockerFixture

from city.models import City
from city.repository.visited_city_repository import VisitedCityRepository


@pytest.fixture
def repo():
    return VisitedCityRepository()


@pytest.fixture
def city():
    return City(id=1)


@pytest.fixture
def user():
    class User:
        id = 1

    return User()


def test_get_average_rating_with_value(mocker: MockerFixture, repo, city):
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
    mock_aggregate = mock_filter.return_value.aggregate
    mock_aggregate.return_value = {'rating__avg': 3.7}

    result = repo.get_average_rating(city.id)

    assert result == 3.5  # округление 3.7 → 3.5
    mock_filter.assert_called_once_with(city_id=city.id)
    mock_aggregate.assert_called_once()


def test_get_average_rating_zero_if_none(mocker: MockerFixture, repo, city):
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
    mock_aggregate = mock_filter.return_value.aggregate
    mock_aggregate.return_value = {'rating__avg': None}

    result = repo.get_average_rating(city.id)

    assert result == 0.0


def test_count_user_visits(mocker: MockerFixture, repo, city, user):
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 4

    result = repo.count_user_visits(city.id, user)

    assert result == 4
    mock_filter.assert_called_once_with(city_id=city.id, user=user)
    mock_count.assert_called_once()


def test_count_all_visits(mocker: MockerFixture, repo, city):
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 15

    result = repo.count_all_visits(city.id)

    assert result == 15
    mock_filter.assert_called_once_with(city_id=city.id)
    mock_count.assert_called_once()


def test_get_popular_months(mocker: MockerFixture, repo, city):
    mock_qs = mocker.MagicMock()
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)

    mock_qs.annotate.return_value = mock_qs
    mock_qs.values.return_value = mock_qs
    mock_qs.annotate.return_value = mock_qs
    mock_qs.order_by.return_value = mock_qs
    mock_qs.values_list.return_value = [5, 6, 7]

    result = repo.get_popular_months(city.id)

    assert result == [5, 6, 7]
    mock_filter.assert_called_once_with(city_id=city.id, date_of_visit__isnull=False)
    mock_qs.annotate.assert_called()
    mock_qs.values.assert_called()
    mock_qs.order_by.assert_called()
    mock_qs.values_list.assert_called_once_with('month', flat=True)


def test_get_user_visits(mocker: MockerFixture, repo, city, user):
    mock_qs = mocker.MagicMock()
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)

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

    result = repo.get_user_visits(city.id, user)

    assert isinstance(result, list)
    assert result[0]['id'] == 1
    assert result[0]['city__title'] == 'Kazan'

    mock_filter.assert_called_once_with(user=user, city_id=city.id)
    mock_qs.select_related.assert_called_once_with('city')
    mock_qs.order_by.assert_called()
    mock_qs.values.assert_called_once_with(
        'id', 'date_of_visit', 'rating', 'impression', 'city__title'
    )


def test_get_number_of_users_who_visit_city(mocker: MockerFixture, repo):
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 7

    city_id = 42
    result = repo.get_number_of_users_who_visit_city(city_id)

    assert result == 7
    mock_filter.assert_called_once_with(city_id=city_id, is_first_visit=True)
    mock_count.assert_called_once()


def test_get_number_of_users_who_visit_city_zero(mocker: MockerFixture, repo):
    # Случай, когда посетителей нет
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 0

    city_id = 999
    result = repo.get_number_of_users_who_visit_city(city_id)

    assert result == 0
    mock_filter.assert_called_once_with(city_id=city_id, is_first_visit=True)
    mock_count.assert_called_once()


def test_count_user_visits_zero(mocker: MockerFixture, repo, city, user):
    """
    Проверяет, что count_user_visits возвращает 0, если у пользователя нет посещений города.
    """
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 0

    result = repo.count_user_visits(city.id, user)

    assert result == 0
    mock_filter.assert_called_once_with(city_id=city.id, user=user)
    mock_count.assert_called_once()


def test_count_all_visits_zero(mocker: MockerFixture, repo, city):
    """
    Проверяет, что count_all_visits возвращает 0, если у города нет посещений.
    """
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter')
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 0

    result = repo.count_all_visits(city.id)

    assert result == 0
    mock_filter.assert_called_once_with(city_id=city.id)
    mock_count.assert_called_once()


def test_get_popular_months_empty(mocker: MockerFixture, repo, city):
    """
    Проверяет, что get_popular_months возвращает пустой список, если нет посещений с датой.
    """
    mock_qs = mocker.MagicMock()
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)
    mock_qs.annotate.return_value = mock_qs
    mock_qs.values.return_value = mock_qs
    mock_qs.annotate.return_value = mock_qs
    mock_qs.order_by.return_value = mock_qs
    mock_qs.values_list.return_value = []

    result = repo.get_popular_months(city.id)

    assert result == []
    mock_filter.assert_called_once_with(city_id=city.id, date_of_visit__isnull=False)
    mock_qs.annotate.assert_called()
    mock_qs.values.assert_called()
    mock_qs.order_by.assert_called()
    mock_qs.values_list.assert_called_once_with('month', flat=True)


def test_get_user_visits_empty(mocker: MockerFixture, repo, city, user):
    """
    Проверяет, что get_user_visits возвращает пустой список, если у пользователя нет посещений города.
    """
    mock_qs = mocker.MagicMock()
    mock_filter = mocker.patch('city.models.VisitedCity.objects.filter', return_value=mock_qs)
    mock_qs.select_related.return_value = mock_qs
    mock_qs.order_by.return_value = mock_qs
    mock_qs.values.return_value = []

    result = repo.get_user_visits(city.id, user)

    assert result == []
    mock_filter.assert_called_once_with(user=user, city_id=city.id)
    mock_qs.select_related.assert_called_once_with('city')
    mock_qs.order_by.assert_called()
    mock_qs.values.assert_called_once_with(
        'id', 'date_of_visit', 'rating', 'impression', 'city__title'
    )
