"""
Тестирует корректность соответствия кода обозначения региона и его текстового представления

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


import pytest

from region.models import TYPES_OF_REGIONS


@pytest.mark.parametrize(
    'code, title', (
        ('R', 'республика'),
        ('K', 'край'),
        ('O', 'область'),
        ('G', 'город федерального значения'),
        ('AOb', 'автономная область'),
        ('AOk', 'автономный округ')
    )
)
def test__type_of_regions(code, title):
    for i in TYPES_OF_REGIONS:
        if i[0] == code:
            assert i[1] == title
