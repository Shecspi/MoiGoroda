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


def test_get_rank_in_country_by_visits(mocker, repo):
    """
    Проверяет, что get_rank_in_country_by_visits возвращает корректный ранг города по количеству посещений в стране.
    """
    mock_city = mocker.Mock(id=42, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)

    ranked_data = [
        {'id': 40, 'rank': 1},
        {'id': 42, 'rank': 2},
        {'id': 50, 'rank': 3},
    ]
    mock_annotate = mocker.patch(
        'city.models.City.objects.filter',
        return_value=mocker.Mock(
            annotate=lambda **kwargs: mocker.Mock(
                values=lambda *args: mocker.Mock(order_by=lambda *args: ranked_data)
            )
        ),
    )

    result = repo.get_rank_in_country_by_visits(city_id=42)

    assert result == 2
    mock_annotate.assert_called_once_with(country_id=1)


def test_get_rank_in_country_by_users(mocker, repo):
    """
    Проверяет, что get_rank_in_country_by_users возвращает корректный ранг города по количеству уникальных пользователей в стране.
    """
    ranked_data = [
        {'id': 1, 'rank': 1},
        {'id': 2, 'rank': 2},
        {'id': 42, 'rank': 3},
    ]

    mocker.patch(
        'city.models.City.objects.annotate',
        return_value=mocker.Mock(
            values=lambda *args: mocker.Mock(order_by=lambda *args: ranked_data)
        ),
    )

    result = repo.get_rank_in_country_by_users(city_id=42)
    assert result == 3


@pytest.mark.parametrize(
    'method_name,ranked_data,expected_rank',
    [
        ('get_rank_in_region_by_visits', [{'id': 2, 'rank': 1}, {'id': 42, 'rank': 2}], 2),
        ('get_rank_in_region_by_users', [{'id': 42, 'rank': 1}, {'id': 3, 'rank': 2}], 1),
    ],
)
def test_get_rank_in_region_methods(mocker, repo, method_name, ranked_data, expected_rank):
    """
    Проверяет, что методы ранжирования по региону (по посещениям и по пользователям) возвращают корректный ранг города.
    """
    mock_city = mocker.Mock(id=42, region='region', country='country')
    mocker.patch('city.models.City.objects.get', return_value=mock_city)

    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data

    mock_filter = mocker.patch('city.models.City.objects.select_related')
    mock_filter.return_value.filter.return_value = mock_queryset

    result = getattr(repo, method_name)(42)
    assert result == expected_rank


def test__get_cities_near_index_centered():
    """
    Проверяет, что _get_cities_near_index корректно возвращает 10 городов, центрированных вокруг нужного индекса.
    """
    items = [{'id': i} for i in range(1, 21)]
    result = CityRepository._get_cities_near_index(items, 10)

    assert len(result) == 10
    assert result[0]['id'] == 6
    assert result[-1]['id'] == 15


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
        def annotate(self, **kwargs): return self
        def values(self, *args, **kwargs): return self
        def order_by(self, *args, **kwargs): return self
        def filter(self, *args, **kwargs): return self
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
        def annotate(self, **kwargs): return self
        def values(self, *args, **kwargs): return self
        def order_by(self, *args, **kwargs): return self
        def filter(self, *args, **kwargs): return self
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
        def annotate(self, **kwargs): return self
        def values(self, *args, **kwargs): return self
        def order_by(self, *args, **kwargs): return self
        def filter(self, *args, **kwargs): return self
    qs_mock = FakeQS(fake_cities)
    mocker.patch('city.models.City.objects.all', return_value=qs_mock)
    result = repo.get_neighboring_cities_by_rank_in_country_by_visits(7)
    assert result == fake_cities


def test_get_rank_in_country_by_visits_returns_0_if_not_found(mocker, repo):
    """
    Проверяет, что если город с заданным id отсутствует в ранжированном списке,
    метод возвращает 0 (город не найден).
    """
    mock_city = mocker.Mock(id=999, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    ranked_data = [{'id': i, 'rank': i} for i in range(1, 10)]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_filter.return_value = mock_queryset
    result = repo.get_rank_in_country_by_visits(999)
    assert result == 0


def test_get_number_of_cities_in_region_by_city_no_region(mocker, repo):
    """
    Проверяет, что если у города не задан регион, метод корректно вызывает фильтрацию
    по region=None и возвращает 0 (нет городов в таком регионе).
    """
    city_id = 123
    mock_get = mocker.patch('city.models.City.objects.get')
    city_instance = mocker.Mock()
    city_instance.region = None
    mock_get.return_value = city_instance
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_count = mock_filter.return_value.count
    mock_count.return_value = 0
    result = repo.get_number_of_cities_in_region_by_city(city_id)
    mock_get.assert_called_once_with(id=city_id)
    mock_filter.assert_called_once_with(region=None)
    mock_count.assert_called_once()
    assert result == 0


def test_get_rank_in_country_by_visits_empty_queryset(mocker, repo):
    """
    Проверяет, что если ранжированный список городов пустой, метод возвращает 0.
    """
    mock_city = mocker.Mock(id=1, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = []
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_filter.return_value = mock_queryset
    result = repo.get_rank_in_country_by_visits(1)
    assert result == 0
