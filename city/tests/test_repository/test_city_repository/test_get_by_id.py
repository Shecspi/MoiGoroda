import pytest

from city.models import City
from city.repository.city_repository import CityRepository


@pytest.fixture
def repo():
    return CityRepository()


def test_get_by_id_returns_city(mocker, repo):
    """
    Проверяет, что get_by_id возвращает объект City, если город с заданным id существует.
    """
    fake_city = mocker.Mock(spec=City)
    mock_get = mocker.patch('city.models.City.objects.get', return_value=fake_city)

    result = repo.get_by_id(city_id=42)

    assert result is fake_city
    mock_get.assert_called_once_with(id=42)


def test_get_by_id_raises_when_not_found(mocker, repo):
    """
    Проверяет, что get_by_id выбрасывает исключение City.DoesNotExist, если город не найден.
    """
    mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

    with pytest.raises(City.DoesNotExist):
        repo.get_by_id(city_id=999)
    assert True


def test_get_by_id_raises_when_multiple_found(mocker, repo):
    """
    Проверяет, что get_by_id выбрасывает исключение City.MultipleObjectsReturned, если найдено несколько городов с одним id.
    """
    mocker.patch('city.models.City.objects.get', side_effect=City.MultipleObjectsReturned)

    with pytest.raises(City.MultipleObjectsReturned):
        repo.get_by_id(city_id=42)