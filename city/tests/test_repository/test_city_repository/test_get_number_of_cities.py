import pytest

from city.models import City
from city.repository.city_repository import CityRepository


@pytest.fixture
def repo():
    return CityRepository()


def test_get_number_of_cities_without_country_code(mocker, repo):
    """
    Проверяет, что get_number_of_cities возвращает общее количество городов, если country_code не указан.
    """
    mock_all = mocker.patch('city.models.City.objects.all')
    mock_count = mock_all.return_value.count
    mock_count.return_value = 10

    result = repo.get_number_of_cities()

    assert result == 10
    mock_all.assert_called_once()
    mock_count.assert_called_once()


def test_get_number_of_cities_with_country_code(mocker, repo):
    """
    Проверяет, что get_number_of_cities возвращает количество городов, отфильтрованных по country_code.
    """
    mock_all = mocker.patch('city.models.City.objects.all')
    mock_filter = mock_all.return_value.filter
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 5

    country_code = 'RU'
    result = repo.get_number_of_cities(country_code=country_code)

    assert result == 5
    mock_all.assert_called_once()
    mock_filter.assert_called_once_with(country__code=country_code)
    mock_count.assert_called_once()


def test_get_number_of_cities_with_country_code_returns_zero_if_none_found(mocker, repo):
    """
    Проверяет, что get_number_of_cities возвращает 0, если по country_code не найдено ни одного города.
    """
    mock_all = mocker.patch('city.models.City.objects.all')
    mock_filter = mock_all.return_value.filter
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 0

    result = repo.get_number_of_cities(country_code='ZZZ')

    assert result == 0
    mock_all.assert_called_once()
    mock_filter.assert_called_once_with(country__code='ZZZ')
    mock_count.assert_called_once()


def test_get_number_of_cities_with_empty_country_code(mocker, repo):
    """
    Проверяет, что get_number_of_cities возвращает общее количество городов, если передан пустой country_code.
    """
    mock_all = mocker.patch('city.models.City.objects.all')
    mock_count = mock_all.return_value.count
    mock_count.return_value = 7

    result = repo.get_number_of_cities(country_code='')

    assert result == 7
    mock_all.assert_called_once()
    mock_count.assert_called_once()


def test_get_number_of_cities_count_raises_exception(mocker, repo):
    """
    Проверяет, что если count выбрасывает исключение, оно пробрасывается дальше.
    """
    mock_all = mocker.patch('city.models.City.objects.all')
    mock_count = mock_all.return_value.count
    mock_count.side_effect = Exception('DB error')

    with pytest.raises(Exception, match='DB error'):
        repo.get_number_of_cities()