import pytest

from city.models import City
from city.repository.city_repository import CityRepository


def test_get_by_id_returns_city(mocker):
    fake_city = mocker.Mock(spec=City)
    mock_get = mocker.patch('city.models.City.objects.get', return_value=fake_city)
    repository = CityRepository()

    result = repository.get_by_id(city_id=42)

    assert result is fake_city
    mock_get.assert_called_once_with(id=42)


def test_get_by_id_raises_when_not_found(mocker):
    mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)

    repository = CityRepository()

    with pytest.raises(City.DoesNotExist):
        repository.get_by_id(city_id=999)
    assert True
