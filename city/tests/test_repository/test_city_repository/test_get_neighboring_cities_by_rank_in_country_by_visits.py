import pytest

from city.models import City
from city.repository.city_repository import CityRepository


@pytest.fixture
def repo():
    return CityRepository()


def test_get_neighboring_cities_returns_empty_if_city_not_found(mocker, repo):
    """
    Проверяет, что если город с заданным id отсутствует в списке городов,
    метод возвращает пустой список.
    """
    mock_city = mocker.Mock(id=999, region=mocker.Mock(id=1), country=mocker.Mock(id=2))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    # Мокаем цепочку, чтобы list(...) возвращал список без нужного города
    fake_cities = [{'id': i, 'rank': i} for i in range(1, 10)]

    class FakeQS(list):
        def annotate(self, **kwargs):
            return self

        def values(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def filter(self, *args, **kwargs):
            return self

    qs_mock = FakeQS(fake_cities)
    mocker.patch('city.models.City.objects.all', return_value=qs_mock)
    result = repo.get_neighboring_cities_by_rank_in_country_by_visits(999)
    assert result == []


def test_get_neighboring_cities_when_city_at_start(mocker, repo):
    """
    Проверяет, что если город находится в начале списка (id=1),
    метод возвращает корректный список соседей (все города, если их меньше 10).
    """
    mock_city = mocker.Mock(id=1, region=mocker.Mock(id=1), country=mocker.Mock(id=2))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    fake_cities = [{'id': i, 'rank': i} for i in range(1, 8)]

    class FakeQS(list):
        def annotate(self, **kwargs):
            return self

        def values(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def filter(self, *args, **kwargs):
            return self

    qs_mock = FakeQS(fake_cities)
    mocker.patch('city.models.City.objects.all', return_value=qs_mock)
    result = repo.get_neighboring_cities_by_rank_in_country_by_visits(1)
    assert result == fake_cities


def test_get_neighboring_cities_when_city_at_end(mocker, repo):
    """
    Проверяет, что если город находится в конце списка (id=7),
    метод возвращает корректный список соседей (все города, если их меньше 10).
    """
    mock_city = mocker.Mock(id=7, region=mocker.Mock(id=1), country=mocker.Mock(id=2))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    fake_cities = [{'id': i, 'rank': i} for i in range(1, 8)]

    class FakeQS(list):
        def annotate(self, **kwargs):
            return self

        def values(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def filter(self, *args, **kwargs):
            return self

    qs_mock = FakeQS(fake_cities)
    mocker.patch('city.models.City.objects.all', return_value=qs_mock)
    result = repo.get_neighboring_cities_by_rank_in_country_by_visits(7)
    assert result == fake_cities






