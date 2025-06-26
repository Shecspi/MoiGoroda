import pytest
from city.models import City
from city.repository.city_repository import CityRepository

@pytest.fixture
def repo():
    return CityRepository()

def test_neighboring_cities_returns_correct_list_with_region(mocker, repo):
    """
    Проверяет, что если у города есть регион, возвращается результат _get_cities_near_index по городам этого региона.
    """
    mock_city = mocker.Mock(id=42, region=mocker.Mock(id=7), country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    mock_queryset = mocker.Mock()
    ranked_cities = [
        {'id': i, 'title': f'City {i}', 'visits': 10-i, 'rank': i} for i in range(1, 21)
    ]
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_cities
    mock_select_related = mocker.patch('city.models.City.objects.select_related')
    mock_select_related.return_value.filter.return_value = mock_queryset
    mock_get_cities_near_index = mocker.patch.object(repo, '_get_cities_near_index', return_value=ranked_cities[5:15])
    result = repo.get_neighboring_cities_by_rank_in_region_by_users(42)
    mock_select_related.assert_called_once_with('region')
    mock_select_related.return_value.filter.assert_called_once_with(region_id=7)
    mock_get_cities_near_index.assert_called_once_with(ranked_cities, 42)
    assert result == ranked_cities[5:15]

def test_neighboring_cities_returns_correct_list_without_region(mocker, repo):
    """
    Проверяет, что если у города нет региона, возвращается результат _get_cities_near_index по городам страны.
    """
    mock_city = mocker.Mock(id=42, region=None, country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    mock_queryset = mocker.Mock()
    ranked_cities = [
        {'id': i, 'title': f'City {i}', 'visits': 10-i, 'rank': i} for i in range(1, 21)
    ]
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_cities
    mock_select_related = mocker.patch('city.models.City.objects.select_related')
    mock_select_related.return_value.filter.return_value = mock_queryset
    mock_get_cities_near_index = mocker.patch.object(repo, '_get_cities_near_index', return_value=ranked_cities[5:15])
    result = repo.get_neighboring_cities_by_rank_in_region_by_users(42)
    mock_select_related.assert_called_once_with('country')
    mock_select_related.return_value.filter.assert_called_once_with(country_id=1)
    mock_get_cities_near_index.assert_called_once_with(ranked_cities, 42)
    assert result == ranked_cities[5:15]

def test_neighboring_cities_city_does_not_exist(mocker, repo):
    """
    Проверяет, что если City.objects.get выбрасывает исключение, метод возвращает пустой список.
    """
    mocker.patch('city.models.City.objects.get', side_effect=City.DoesNotExist)
    result = repo.get_neighboring_cities_by_rank_in_region_by_users(123)
    assert result == []

def test_neighboring_cities_multiple_objects_returned(mocker, repo):
    """
    Проверяет, что если City.objects.get выбрасывает MultipleObjectsReturned, метод возвращает пустой список.
    """
    mocker.patch('city.models.City.objects.get', side_effect=City.MultipleObjectsReturned)
    result = repo.get_neighboring_cities_by_rank_in_region_by_users(123)
    assert result == []

def test_neighboring_cities_empty_ranked_list(mocker, repo):
    """
    Проверяет, что если ранжированный список пуст, _get_cities_near_index вызывается с пустым списком и возвращает пустой список.
    """
    mock_city = mocker.Mock(id=42, region=mocker.Mock(id=7), country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    mock_queryset = mocker.Mock()
    ranked_cities = []
    mock_queryset.annotate.return_value.values.return_value.order_by.return_value = ranked_cities
    mock_select_related = mocker.patch('city.models.City.objects.select_related')
    mock_select_related.return_value.filter.return_value = mock_queryset
    mock_get_cities_near_index = mocker.patch.object(repo, '_get_cities_near_index', return_value=[])
    result = repo.get_neighboring_cities_by_rank_in_region_by_users(42)
    mock_get_cities_near_index.assert_called_once_with(ranked_cities, 42)
    assert result == []

def test_neighboring_cities_orm_methods_called(mocker, repo):
    """
    Проверяет, что методы ORM вызываются в правильной последовательности.
    """
    mock_city = mocker.Mock(id=42, region=mocker.Mock(id=7), country=mocker.Mock(id=1))
    mocker.patch('city.models.City.objects.get', return_value=mock_city)
    mock_queryset = mocker.Mock()
    annotate = mock_queryset.annotate
    values = annotate.return_value.values
    order_by = values.return_value.order_by
    order_by.return_value = [{'id': 42, 'rank': 1}]
    select_related = mocker.patch('city.models.City.objects.select_related')
    select_related.return_value.filter.return_value = mock_queryset
    mock_get_cities_near_index = mocker.patch.object(repo, '_get_cities_near_index', return_value=[{'id': 42, 'rank': 1}])
    repo.get_neighboring_cities_by_rank_in_region_by_users(42)
    select_related.assert_called()
    annotate.assert_called()
    values.assert_called()
    order_by.assert_called()
    mock_get_cities_near_index.assert_called_once() 