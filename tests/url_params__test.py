"""
Тестирует генерацию параметров URL для сортировки и фильтрации.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from services.url_params import make_url_params


def test__url_params_empty():
    assert make_url_params() == ''


def test__url_params_filter_is_none():
    filter_value = None
    assert make_url_params(filter_value=filter_value) == ''


def test__url_params_sort_is_none():
    sort_value = None
    assert make_url_params(sort_value=sort_value) == ''


def test__url_params_only_filter():
    filter_value = 'new'
    assert make_url_params(filter_value=filter_value) == f'filter={filter_value}'


def test__url_params_only_sort():
    sort_value = 'new'
    assert make_url_params(sort_value=sort_value) == f'sort={sort_value}'


def test__url_params_filter_is_none_and_sort():
    filter_value = None
    sort_value = 'new_sort'
    assert make_url_params(filter_value=filter_value, sort_value=sort_value) == f'sort={sort_value}'


def test__url_params_filter_and_sort_is_none():
    filter_value = 'new_sort'
    sort_value = None
    assert (
        make_url_params(filter_value=filter_value, sort_value=sort_value)
        == f'filter={filter_value}'
    )


def test__url_params_filter():
    filter_value = 'new_filter'
    sort_value = 'new_sort'
    assert (
        make_url_params(filter_value, sort_value=sort_value)
        == f'filter={filter_value}&sort={sort_value}'
    )
