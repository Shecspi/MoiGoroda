import pytest
from city.repository.city_repository import CityRepository

@pytest.fixture
def repo():
    return CityRepository()

def test_get_rank_in_country_by_users_returns_rank_if_found(mocker, repo):
    """
    Проверяет, что если город найден в ранжированном списке, возвращается его ранг.
    """
    ranked_data = [
        {'id': 1, 'rank': 1},
        {'id': 5, 'rank': 3},
        {'id': 7, 'rank': 2},
    ]
    mock_queryset = mocker.patch('city.models.City.objects.annotate')
    mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data
    result = repo.get_rank_in_country_by_users(5)
    assert result == 3

def test_get_rank_in_country_by_users_returns_zero_if_not_found(mocker, repo):
    """
    Проверяет, что если город с заданным id отсутствует в ранжированном списке, метод возвращает 0.
    """
    ranked_data = [
        {'id': 1, 'rank': 1},
        {'id': 2, 'rank': 2},
    ]
    mock_queryset = mocker.patch('city.models.City.objects.annotate')
    mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data
    result = repo.get_rank_in_country_by_users(99)
    assert result == 0

def test_get_rank_in_country_by_users_empty_ranked_data(mocker, repo):
    """
    Проверяет, что если ранжированный список пуст, возвращается 0.
    """
    ranked_data = []
    mock_queryset = mocker.patch('city.models.City.objects.annotate')
    mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data
    result = repo.get_rank_in_country_by_users(5)
    assert result == 0

def test_get_rank_in_country_by_users_duplicate_ids(mocker, repo):
    """
    Проверяет, что если в ранжированном списке несколько городов с одинаковым id, возвращается ранг первого найденного.
    """
    ranked_data = [
        {'id': 5, 'rank': 2},
        {'id': 5, 'rank': 3},
    ]
    mock_queryset = mocker.patch('city.models.City.objects.annotate')
    mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data
    result = repo.get_rank_in_country_by_users(5)
    assert result == 2

def test_get_rank_in_country_by_users_rank_is_none(mocker, repo):
    """
    Проверяет, что если у найденного города rank=None, возвращается None.
    (Поведение метода: возвращает None, если rank=None)
    """
    ranked_data = [{'id': 5, 'rank': None}]
    mock_queryset = mocker.patch('city.models.City.objects.annotate')
    mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data
    result = repo.get_rank_in_country_by_users(5)
    assert result is None

def test_get_rank_in_country_by_users_dict_without_id(mocker, repo):
    """
    Проверяет, что если в ранжированном списке словарь без ключа id, выбрасывается KeyError.
    (Поведение метода: выбрасывает KeyError)
    """
    ranked_data = [{'rank': 1}]
    mock_queryset = mocker.patch('city.models.City.objects.annotate')
    mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data
    with pytest.raises(KeyError):
        repo.get_rank_in_country_by_users(5)

def test_get_rank_in_country_by_users_dict_without_rank(mocker, repo):
    """
    Проверяет, что если в ранжированном списке словарь без ключа rank, выбрасывается KeyError.
    (Поведение метода: выбрасывает KeyError)
    """
    ranked_data = [{'id': 5}]
    mock_queryset = mocker.patch('city.models.City.objects.annotate')
    mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data
    with pytest.raises(KeyError):
        repo.get_rank_in_country_by_users(5)

def test_get_rank_in_country_by_users_non_dict_in_list(mocker, repo):
    """
    Проверяет, что если в ранжированном списке не словарь, а строка/число, выбрасывается TypeError.
    (Поведение метода: выбрасывает TypeError)
    """
    ranked_data = ['not a dict', 123]
    mock_queryset = mocker.patch('city.models.City.objects.annotate')
    mock_queryset.return_value.values.return_value.order_by.return_value = ranked_data
    with pytest.raises(TypeError):
        repo.get_rank_in_country_by_users(5)

def test_get_rank_in_country_by_users_orm_methods_called(mocker, repo):
    """
    Проверяет, что методы ORM вызываются в правильной последовательности.
    """
    mock_annotate = mocker.patch('city.models.City.objects.annotate')
    mock_values = mock_annotate.return_value.values
    mock_order_by = mock_values.return_value.order_by
    mock_order_by.return_value = [{'id': 5, 'rank': 1}]
    repo.get_rank_in_country_by_users(5)
    mock_annotate.assert_called_once()
    mock_values.assert_called_once()
    mock_order_by.assert_called_once() 