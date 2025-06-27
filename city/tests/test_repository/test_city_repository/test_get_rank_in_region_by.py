import pytest

from city.models import City
from city.repository.city_repository import CityRepository


@pytest.fixture
def repo():
    return CityRepository()


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

def test_get_rank_in_region_returns_none_if_city_not_in_ranked_data(mocker, repo):
    """
    Проверяет, что если город с данным id отсутствует в ранжированном списке, метод возвращает 0.
    """
    mock_city = mocker.Mock(id=99, region='region', country='country')
    mocker.patch('city.models.City.objects.get', return_value=mock_city)

    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = [
        {'id': 1, 'rank': 1}, {'id': 2, 'rank': 2}
    ]
    mock_filter = mocker.patch('city.models.City.objects.select_related')
    mock_filter.return_value.filter.return_value = mock_queryset

    result = repo.get_rank_in_region_by_visits(99)
    assert result == 0
    result = repo.get_rank_in_region_by_users(99)
    assert result == 0

def test_get_rank_in_region_empty_ranked_data(mocker, repo):
    """
    Проверяет, что если ранжированный список пуст, метод возвращает 0.
    """
    mock_city = mocker.Mock(id=42, region='region', country='country')
    mocker.patch('city.models.City.objects.get', return_value=mock_city)

    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = []
    mock_filter = mocker.patch('city.models.City.objects.select_related')
    mock_filter.return_value.filter.return_value = mock_queryset

    result = repo.get_rank_in_region_by_visits(42)
    assert result == 0
    result = repo.get_rank_in_region_by_users(42)
    assert result == 0

def test_get_rank_in_region_city_does_not_exist(mocker, repo):
    """
    Проверяет, что если City.objects.get выбрасывает исключение, метод возвращает 0.
    """
    mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)
    assert repo.get_rank_in_region_by_visits(123) == 0
    assert repo.get_rank_in_region_by_users(123) == 0

def test_get_rank_in_region_orm_methods_called(mocker, repo):
    """
    Проверяет, что методы ORM вызываются в правильной последовательности.
    """
    mock_city = mocker.Mock(id=42, region='region', country='country')
    mocker.patch('city.models.City.objects.get', return_value=mock_city)

    mock_queryset = mocker.Mock()
    annotate = mock_queryset.annotate
    values = annotate.return_value.values
    order_by = values.return_value.order_by
    order_by.return_value = [{'id': 42, 'rank': 1}]

    select_related = mocker.patch('city.models.City.objects.select_related')
    select_related.return_value.filter.return_value = mock_queryset

    repo.get_rank_in_region_by_visits(42)
    repo.get_rank_in_region_by_users(42)
    select_related.assert_called()
    annotate.assert_called()
    values.assert_called()
    order_by.assert_called()

def test_get_rank_in_region_returns_first_if_duplicate_ids(mocker, repo):
    """
    Проверяет, что если в ранжированном списке несколько городов с одинаковым id, возвращается ранг первого найденного.
    """
    mock_city = mocker.Mock(id=42, region='region', country='country')
    mocker.patch('city.models.City.objects.get', return_value=mock_city)

    ranked_data = [
        {'id': 42, 'rank': 2},
        {'id': 42, 'rank': 3},
    ]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.select_related')
    mock_filter.return_value.filter.return_value = mock_queryset

    result = repo.get_rank_in_region_by_visits(42)
    assert result == 2
    result = repo.get_rank_in_region_by_users(42)
    assert result == 2

def test_get_rank_in_region_rank_is_none(mocker, repo):
    """
    Проверяет, что если у найденного города rank=None, возвращается None.
    (Поведение метода: возвращает None, если rank=None)
    """
    mock_city = mocker.Mock(id=42, region='region', country='country')
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    ranked_data = [{'id': 42, 'rank': None}]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.select_related')
    mock_filter.return_value.filter.return_value = mock_queryset
    result = repo.get_rank_in_region_by_visits(42)
    assert result is None
    result = repo.get_rank_in_region_by_users(42)
    assert result is None

def test_get_rank_in_region_dict_without_id(mocker, repo):
    """
    Проверяет, что если в ранжированном списке словарь без ключа id, выбрасывается KeyError.
    (Поведение метода: выбрасывает KeyError)
    """
    mock_city = mocker.Mock(id=42, region='region', country='country')
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    ranked_data = [{'rank': 1}]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.select_related')
    mock_filter.return_value.filter.return_value = mock_queryset
    with pytest.raises(KeyError):
        repo.get_rank_in_region_by_visits(42)
    with pytest.raises(KeyError):
        repo.get_rank_in_region_by_users(42)

def test_get_rank_in_region_dict_without_rank(mocker, repo):
    """
    Проверяет, что если в ранжированном списке словарь без ключа rank, выбрасывается KeyError.
    (Поведение метода: выбрасывает KeyError)
    """
    mock_city = mocker.Mock(id=42, region='region', country='country')
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    ranked_data = [{'id': 42}]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.select_related')
    mock_filter.return_value.filter.return_value = mock_queryset
    with pytest.raises(KeyError):
        repo.get_rank_in_region_by_visits(42)
    with pytest.raises(KeyError):
        repo.get_rank_in_region_by_users(42)

def test_get_rank_in_region_non_dict_in_list(mocker, repo):
    """
    Проверяет, что если в ранжированном списке не словарь, а строка/число, выбрасывается TypeError.
    (Поведение метода: выбрасывает TypeError)
    """
    mock_city = mocker.Mock(id=42, region='region', country='country')
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    ranked_data = ['not a dict', 123]
    mock_queryset = mocker.Mock()
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_data
    mock_filter = mocker.patch('city.models.City.objects.select_related')
    mock_filter.return_value.filter.return_value = mock_queryset
    with pytest.raises(TypeError):
        repo.get_rank_in_region_by_visits(42)
    with pytest.raises(TypeError):
        repo.get_rank_in_region_by_users(42)