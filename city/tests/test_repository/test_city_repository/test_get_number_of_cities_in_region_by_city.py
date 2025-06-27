import pytest

from city.models import City
from city.repository.city_repository import CityRepository


@pytest.fixture
def repo():
    return CityRepository()


def test_get_number_of_cities_in_region_by_city_success(mocker, repo):
    """
    Проверяет, что get_number_of_cities_in_region_by_city возвращает количество городов в том же регионе, что и указанный город.
    """
    city_id = 123

    # Мокаем City.objects.get
    mock_get = mocker.patch('city.models.City.objects.get')
    city_instance = mocker.Mock()
    city_instance.region = 'region_1'
    mock_get.return_value = city_instance

    # Мокаем City.objects.filter(...).count()
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 7

    result = repo.get_number_of_cities_in_region_by_city(city_id)

    assert result == 7
    mock_get.assert_called_once_with(id=city_id)
    mock_filter.assert_called_once_with(region=city_instance.region)
    mock_count.assert_called_once()


@pytest.mark.parametrize('exception', [City.DoesNotExist, City.MultipleObjectsReturned])
def test_get_number_of_cities_in_region_by_city_exceptions(mocker, repo, exception):
    """
    Проверяет, что get_number_of_cities_in_region_by_city возвращает 0, если город не найден или найдено несколько городов.
    """
    city_id = 999
    mock_get = mocker.patch('city.models.City.objects.get')
    mock_get.side_effect = exception

    result = repo.get_number_of_cities_in_region_by_city(city_id)

    assert result == 0
    mock_get.assert_called_once_with(id=city_id)


def test_get_number_of_cities_in_region_by_city_with_none_region(mocker, repo):
    """
    Проверяет, что если у города не задан регион, фильтр вызывается с region=None.
    """
    city_id = 123
    mock_get = mocker.patch('city.models.City.objects.get')
    city_instance = mocker.Mock()
    city_instance.region = None
    mock_get.return_value = city_instance

    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 3

    result = repo.get_number_of_cities_in_region_by_city(city_id)

    assert result == 3
    mock_get.assert_called_once_with(id=city_id)
    mock_filter.assert_called_once_with(region=None)
    mock_count.assert_called_once()


def test_get_number_of_cities_in_region_by_city_zero_cities(mocker, repo):
    """
    Проверяет, что если в регионе нет городов, возвращается 0.
    """
    city_id = 123
    mock_get = mocker.patch('city.models.City.objects.get')
    city_instance = mocker.Mock()
    city_instance.region = 'region_1'
    mock_get.return_value = city_instance

    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 0

    result = repo.get_number_of_cities_in_region_by_city(city_id)

    assert result == 0
    mock_get.assert_called_once_with(id=city_id)
    mock_filter.assert_called_once_with(region=city_instance.region)
    mock_count.assert_called_once()


def test_get_number_of_cities_in_region_by_city_count_raises(mocker, repo):
    """
    Проверяет, что если count выбрасывает исключение, оно пробрасывается дальше.
    """
    city_id = 123
    mock_get = mocker.patch('city.models.City.objects.get')
    city_instance = mocker.Mock()
    city_instance.region = 'region_1'
    mock_get.return_value = city_instance

    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_count = mock_filter.return_value.count
    mock_count.side_effect = Exception('DB error')

    with pytest.raises(Exception, match='DB error'):
        repo.get_number_of_cities_in_region_by_city(city_id)