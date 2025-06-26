import pytest

from city.models import City
from city.repository.city_repository import CityRepository


@pytest.fixture
def repo():
    return CityRepository()


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


def test_get_rank_in_country_by_visits_returns_rank_if_found(mocker, repo):
    """
    Проверяет, что если город найден в ранжированном списке, возвращается его ранг.
    """
    mock_city = mocker.Mock(id=5, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    ranked_data = [{'id': 1, 'rank': 1}, {'id': 5, 'rank': 3}, {'id': 7, 'rank': 2}]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_filter.return_value = mock_queryset
    result = repo.get_rank_in_country_by_visits(5)
    assert result == 3


def test_get_rank_in_country_by_visits_empty_ranked_data(mocker, repo):
    """
    Проверяет, что если ранжированный список пуст, возвращается 0.
    """
    mock_city = mocker.Mock(id=5, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = []
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_filter.return_value = mock_queryset
    result = repo.get_rank_in_country_by_visits(5)
    assert result == 0


def test_get_rank_in_country_by_visits_city_does_not_exist(mocker, repo):
    """
    Проверяет, что если City.objects.get выбрасывает исключение, метод пробрасывает его дальше.
    """
    mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)
    with pytest.raises(City.DoesNotExist):
        repo.get_rank_in_country_by_visits(123)


def test_get_rank_in_country_by_visits_duplicate_ids(mocker, repo):
    """
    Проверяет, что если в ранжированном списке несколько городов с одинаковым id, возвращается ранг первого найденного.
    """
    mock_city = mocker.Mock(id=5, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    ranked_data = [
        {'id': 5, 'rank': 2},
        {'id': 5, 'rank': 3},
    ]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_filter.return_value = mock_queryset
    result = repo.get_rank_in_country_by_visits(5)
    assert result == 2


def test_get_rank_in_country_by_visits_rank_is_none(mocker, repo):
    """
    Проверяет, что если у найденного города rank=None, возвращается 0.
    """
    mock_city = mocker.Mock(id=5, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    ranked_data = [{'id': 5, 'rank': None}]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_filter.return_value = mock_queryset
    result = repo.get_rank_in_country_by_visits(5)
    assert result == 0


def test_get_rank_in_country_by_visits_dict_without_id(mocker, repo):
    """
    Проверяет, что если в ранжированном списке словарь без ключа id, возвращается 0.
    """
    mock_city = mocker.Mock(id=5, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    ranked_data = [{'rank': 1}]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_filter.return_value = mock_queryset
    result = repo.get_rank_in_country_by_visits(5)
    assert result == 0


def test_get_rank_in_country_by_visits_dict_without_rank(mocker, repo):
    """
    Проверяет, что если в ранжированном списке словарь без ключа rank, возвращается 0.
    """
    mock_city = mocker.Mock(id=5, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    ranked_data = [{'id': 5}]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_filter.return_value = mock_queryset
    result = repo.get_rank_in_country_by_visits(5)
    assert result == 0


def test_get_rank_in_country_by_visits_non_dict_in_list(mocker, repo):
    """
    Проверяет, что если в ранжированном списке не словарь, а строка/число, возвращается 0.
    """
    mock_city = mocker.Mock(id=5, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    ranked_data = ['not a dict', 123]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_filter.return_value = mock_queryset
    result = repo.get_rank_in_country_by_visits(5)
    assert result == 0


def test_get_rank_in_country_by_visits_orm_methods_called(mocker, repo):
    """
    Проверяет, что методы ORM вызываются в правильной последовательности.
    """
    mock_city = mocker.Mock(id=5, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    mock_queryset = mocker.Mock()
    annotate = mock_queryset.annotate
    values = annotate.return_value.values
    order_by = values.return_value.order_by
    order_by.return_value = [{'id': 5, 'rank': 1}]
    mock_filter = mocker.patch('city.models.City.objects.filter')
    mock_filter.return_value = mock_queryset
    repo.get_rank_in_country_by_visits(5)
    mock_filter.assert_called_once()
    annotate.assert_called()
    values.assert_called()
    order_by.assert_called()


def test_nonexistent_city_raises_exception(mocker, repo):
    """
    Если get_by_id выбрасывает исключение (город не найден), функция также выбрасывает исключение.
    """
    mocker.patch.object(repo, 'get_by_id', side_effect=Exception('Not found'))
    # City.objects.filter не должен вызываться
    mocker.patch('city.models.City.objects.filter')
    with pytest.raises(Exception) as excinfo:
        repo.get_rank_in_country_by_visits(999)
    assert str(excinfo.value) == 'Not found'


def test_only_cities_from_same_country_are_ranked(mocker, repo):
    """
    Проверяет, что учитываются только города из нужной страны.
    """
    mock_country = mocker.Mock(id=1)
    mock_city = mocker.Mock(id=42, country=mock_country)
    mocker.patch.object(repo, 'get_by_id', return_value=mock_city)

    # Только города из страны 1 должны быть в выдаче
    ranked_cities = [
        {'id': 40, 'title': 'A', 'visits': 10, 'rank': 1},
        {'id': 42, 'title': 'B', 'visits': 5, 'rank': 2},
        {'id': 50, 'title': 'C', 'visits': 2, 'rank': 3},
    ]
    mock_queryset = mocker.Mock()
    mock_annotate = mocker.Mock()
    mock_values = mocker.Mock()
    mock_order_by = mocker.Mock(return_value=ranked_cities)
    mock_values.order_by = mock_order_by
    mock_annotate.values = mocker.Mock(return_value=mock_values)
    mock_queryset.annotate = mocker.Mock(return_value=mock_annotate)
    filter_patch = mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)

    result = repo.get_rank_in_country_by_visits(42)
    filter_patch.assert_called_once_with(country_id=1)
    assert result == 2


def test_returns_zero_if_city_not_in_ranked_list(mocker, repo):
    """
    Если город не найден в списке ранжирования, возвращается 0.
    """
    mock_country = mocker.Mock(id=1)
    mock_city = mocker.Mock(id=99, country=mock_country)
    mocker.patch.object(repo, 'get_by_id', return_value=mock_city)
    # В выдаче нет города с id=99
    ranked_cities = [
        {'id': 40, 'title': 'A', 'visits': 10, 'rank': 1},
        {'id': 42, 'title': 'B', 'visits': 5, 'rank': 2},
    ]
    mock_queryset = mocker.Mock()
    mock_annotate = mocker.Mock()
    mock_values = mocker.Mock()
    mock_order_by = mocker.Mock(return_value=ranked_cities)
    mock_values.order_by = mock_order_by
    mock_annotate.values = mocker.Mock(return_value=mock_values)
    mock_queryset.annotate = mocker.Mock(return_value=mock_annotate)
    mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)
    assert repo.get_rank_in_country_by_visits(99) == 0


def test_returns_zero_if_no_cities(mocker, repo):
    """
    Если в стране нет ни одного города, возвращается 0.
    """
    mock_country = mocker.Mock(id=1)
    mock_city = mocker.Mock(id=1, country=mock_country)
    mocker.patch.object(repo, 'get_by_id', return_value=mock_city)
    mock_queryset = mocker.Mock()
    mock_annotate = mocker.Mock()
    mock_values = mocker.Mock()
    mock_order_by = mocker.Mock(return_value=[])
    mock_values.order_by = mock_order_by
    mock_annotate.values = mocker.Mock(return_value=mock_values)
    mock_queryset.annotate = mocker.Mock(return_value=mock_annotate)
    mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)
    assert repo.get_rank_in_country_by_visits(1) == 0


def test_duplicate_visits_do_not_affect_rank(mocker, repo):
    """
    Проверяет, что если у города несколько посещений, ранг считается корректно.
    """
    mock_country = mocker.Mock(id=1)
    mock_city = mocker.Mock(id=42, country=mock_country)
    mocker.patch.object(repo, 'get_by_id', return_value=mock_city)
    # У города 42 больше посещений, он выше в рейтинге
    ranked_cities = [
        {'id': 42, 'title': 'B', 'visits': 20, 'rank': 1},
        {'id': 40, 'title': 'A', 'visits': 10, 'rank': 2},
        {'id': 50, 'title': 'C', 'visits': 2, 'rank': 3},
    ]
    mock_queryset = mocker.Mock()
    mock_annotate = mocker.Mock()
    mock_values = mocker.Mock()
    mock_order_by = mocker.Mock(return_value=ranked_cities)
    mock_values.order_by = mock_order_by
    mock_annotate.values = mocker.Mock(return_value=mock_values)
    mock_queryset.annotate = mocker.Mock(return_value=mock_annotate)
    mocker.patch('city.models.City.objects.filter', return_value=mock_queryset)
    assert repo.get_rank_in_country_by_visits(42) == 1


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