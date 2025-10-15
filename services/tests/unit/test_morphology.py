"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from services.morphology import (
    to_accusative,
    to_dative,
    to_genitive,
    to_instrumental,
    to_nominative,
    to_prepositional,
    plural_by_number,
)


@pytest.mark.unit
def test_to_nominative() -> None:
    """Тест склонения в именительный падеж"""
    assert to_nominative('Россия') == 'Россия'
    assert to_nominative('Франция') == 'Франция'
    assert to_nominative('Китай') == 'Китай'


@pytest.mark.unit
def test_to_genitive() -> None:
    """Тест склонения в родительный падеж"""
    assert to_genitive('Россия') == 'России'
    assert to_genitive('Франция') == 'Франции'
    assert to_genitive('Китай') == 'Китая'


@pytest.mark.unit
def test_to_dative() -> None:
    """Тест склонения в дательный падеж"""
    assert to_dative('Россия') == 'России'
    assert to_dative('Франция') == 'Франции'
    assert to_dative('Китай') == 'Китаю'


@pytest.mark.unit
def test_to_accusative() -> None:
    """Тест склонения в винительный падеж"""
    assert to_accusative('Россия') == 'Россию'
    assert to_accusative('Франция') == 'Францию'
    assert to_accusative('Китай') == 'Китай'


@pytest.mark.unit
def test_to_instrumental() -> None:
    """Тест склонения в творительный падеж"""
    assert to_instrumental('Россия') == 'Россией'
    assert to_instrumental('Франция') == 'Францией'
    assert to_instrumental('Китай') == 'Китаем'


@pytest.mark.unit
def test_to_prepositional() -> None:
    """Тест склонения в предложный падеж"""
    assert to_prepositional('Россия') == 'России'
    assert to_prepositional('Франция') == 'Франции'
    assert to_prepositional('Китай') == 'Китае'


@pytest.mark.unit
def test_to_genitive_with_phrase() -> None:
    """Тест склонения фразы в родительный падеж"""
    # pymorphy3 склоняет "Санкт-Петербург" как "Санкта-Петербурга"
    assert to_genitive('Санкт-Петербург') == 'Санкта-Петербурга'
    assert to_genitive('Нью-Йорк') == 'Нью-Йорка'


@pytest.mark.unit
def test_to_prepositional_with_phrase() -> None:
    """Тест склонения фразы в предложный падеж"""
    # pymorphy3 склоняет "Санкт-Петербург" как "Санкте-Петербурге"
    assert to_prepositional('Санкт-Петербург') == 'Санкте-Петербурге'
    assert to_prepositional('Нью-Йорк') == 'Нью-Йорке'


@pytest.mark.unit
def test_plural_by_number_1() -> None:
    """Тест множественного числа для 1"""
    assert plural_by_number('город', 1) == 'город'
    assert plural_by_number('страна', 1) == 'страна'


@pytest.mark.unit
def test_plural_by_number_2() -> None:
    """Тест множественного числа для 2"""
    assert plural_by_number('город', 2) == 'города'
    assert plural_by_number('страна', 2) == 'страны'


@pytest.mark.unit
def test_plural_by_number_5() -> None:
    """Тест множественного числа для 5"""
    assert plural_by_number('город', 5) == 'городов'
    assert plural_by_number('страна', 5) == 'стран'


@pytest.mark.unit
def test_plural_by_number_11() -> None:
    """Тест множественного числа для 11"""
    assert plural_by_number('город', 11) == 'городов'
    assert plural_by_number('страна', 11) == 'стран'


@pytest.mark.unit
def test_plural_by_number_21() -> None:
    """Тест множественного числа для 21"""
    assert plural_by_number('город', 21) == 'город'
    assert plural_by_number('страна', 21) == 'страна'


@pytest.mark.unit
def test_plural_by_number_22() -> None:
    """Тест множественного числа для 22"""
    assert plural_by_number('город', 22) == 'города'
    assert plural_by_number('страна', 22) == 'страны'


@pytest.mark.unit
def test_plural_by_number_25() -> None:
    """Тест множественного числа для 25"""
    assert plural_by_number('город', 25) == 'городов'
    assert plural_by_number('страна', 25) == 'стран'


@pytest.mark.unit
def test_plural_by_number_101() -> None:
    """Тест множественного числа для 101"""
    assert plural_by_number('город', 101) == 'город'
    assert plural_by_number('страна', 101) == 'страна'


@pytest.mark.unit
def test_plural_by_number_102() -> None:
    """Тест множественного числа для 102"""
    assert plural_by_number('город', 102) == 'города'
    assert plural_by_number('страна', 102) == 'страны'


@pytest.mark.unit
def test_plural_by_number_105() -> None:
    """Тест множественного числа для 105"""
    assert plural_by_number('город', 105) == 'городов'
    assert plural_by_number('страна', 105) == 'стран'


@pytest.mark.unit
def test_plural_by_number_111() -> None:
    """Тест множественного числа для 111"""
    assert plural_by_number('город', 111) == 'городов'
    assert plural_by_number('страна', 111) == 'стран'


@pytest.mark.unit
def test_plural_by_number_negative() -> None:
    """Тест множественного числа для отрицательных чисел"""
    assert plural_by_number('город', -1) == 'город'
    assert plural_by_number('город', -2) == 'города'
    assert plural_by_number('город', -5) == 'городов'
