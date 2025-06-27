import pytest

from city.models import City
from city.repository.city_repository import CityRepository

def make_items(n):
    return [{'id': i} for i in range(n)]


def test__get_cities_near_index_centered():
    """
    Проверяет, что _get_cities_near_index корректно возвращает 10 городов, центрированных вокруг нужного индекса (пример: индекс 10 из 20).
    """
    items = [{'id': i} for i in range(1, 21)]
    result = CityRepository._get_cities_near_index(items, 10)

    assert len(result) == 10
    assert result[0]['id'] == 6
    assert result[-1]['id'] == 15

def test_get_cities_near_index_short_list():
    """
    Проверяет, что если элементов меньше 10, возвращается весь список.
    """
    items = make_items(5)
    result = CityRepository._get_cities_near_index(items, 2)
    assert result == items

def test_get_cities_near_index_exact_10():
    """
    Проверяет, что если элементов ровно 10, возвращается весь список.
    """
    items = make_items(10)
    result = CityRepository._get_cities_near_index(items, 5)
    assert result == items

def test_get_cities_near_index_index_at_start():
    """
    Проверяет, что если индекс в начале списка, возвращаются первые 10 элементов.
    """
    items = make_items(20)
    result = CityRepository._get_cities_near_index(items, 0)
    assert result == items[:10]

def test_get_cities_near_index_index_at_end():
    """
    Проверяет, что если индекс в конце списка, возвращаются последние 10 элементов.
    """
    items = make_items(20)
    result = CityRepository._get_cities_near_index(items, 19)
    assert result == items[-10:]

def test_get_cities_near_index_index_negative():
    """
    Проверяет, что если индекс отрицательный, возвращается пустой список.
    """
    items = make_items(20)
    result = CityRepository._get_cities_near_index(items, -5)
    assert result == []

def test_get_cities_near_index_index_too_large():
    """
    Проверяет, что если индекс больше или равен длине списка, возвращается пустой список.
    """
    items = make_items(20)
    result = CityRepository._get_cities_near_index(items, 100)
    assert result == []

def test_get_cities_near_index_empty_list():
    """
    Проверяет, что если список пустой, возвращается пустой список.
    """
    items = []
    result = CityRepository._get_cities_near_index(items, 0)
    assert result == []

def test_get_cities_near_index_one_element():
    """
    Проверяет, что если в списке один элемент, возвращается этот элемент.
    """
    items = make_items(1)
    result = CityRepository._get_cities_near_index(items, 0)
    assert result == items

def test_get_cities_near_index_11_elements_middle():
    """
    Проверяет, что при 11 элементах и индексе 5 возвращаются элементы с 1 по 10 (центрирование сдвигается, чтобы не выйти за границы).
    """
    items = make_items(11)
    result = CityRepository._get_cities_near_index(items, 5)
    assert len(result) == 10
    assert result == items[1:11]

def test_get_cities_near_index_index_just_in_range():
    """
    Проверяет, что при индексе 9 из 20 возвращается корректное окно из 10 элементов (с 5 по 14).
    """
    items = make_items(20)
    result = CityRepository._get_cities_near_index(items, 9)
    assert len(result) == 10
    assert result[0]['id'] == 5
    assert result[-1]['id'] == 14