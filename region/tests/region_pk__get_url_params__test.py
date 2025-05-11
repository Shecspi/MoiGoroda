"""
Тестирует работу метода генерации параметров URL для страницы городов конкретного региона.
Страница тестирования '/region/<id>'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from utils.CitiesByRegionMixin import CitiesByRegionMixin


@pytest.mark.parametrize(
    'sort_value, filter_value, expected_value',
    (
        ('', 'magnet', 'filter=magnet'),
        ('', 'current_year', 'filter=current_year'),
        ('', 'last_year', 'filter=last_year'),
        ('name_down', 'magnet', 'filter=magnet&sort=name_down'),
        ('name_down', 'current_year', 'filter=current_year&sort=name_down'),
        ('name_down', 'last_year', 'filter=last_year&sort=name_down'),
        ('name_up', 'magnet', 'filter=magnet&sort=name_up'),
        ('name_up', 'current_year', 'filter=current_year&sort=name_up'),
        ('name_up', 'last_year', 'filter=last_year&sort=name_up'),
        ('date_down', 'magnet', 'filter=magnet&sort=date_down'),
        ('date_down', 'current_year', 'filter=current_year&sort=date_down'),
        ('date_down', 'last_year', 'filter=last_year&sort=date_down'),
        ('date_up', 'magnet', 'filter=magnet&sort=date_up'),
        ('date_up', 'current_year', 'filter=current_year&sort=date_up'),
        ('date_up', 'last_year', 'filter=last_year&sort=date_up'),
        ('default_auth', 'magnet', 'filter=magnet&sort=default_auth'),
        ('default_auth', 'current_year', 'filter=current_year&sort=default_auth'),
        ('default_auth', 'last_year', 'filter=last_year&sort=default_auth'),
        ('default_guest', 'magnet', 'filter=magnet&sort=default_guest'),
        ('default_guest', 'current_year', 'filter=current_year&sort=default_guest'),
        ('default_guest', 'last_year', 'filter=last_year&sort=default_guest'),
    ),
)
def test__get_url_params(sort_value, filter_value, expected_value):
    mixin = CitiesByRegionMixin()
    assert mixin.get_url_params(filter_value, sort_value) == expected_value
