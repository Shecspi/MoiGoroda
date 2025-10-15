"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from services.word_modifications.region import (
    modification__region__accusative_case,
    modification__region__prepositional_case,
)


@pytest.mark.unit
def test_modification__region__accusative_case_1() -> None:
    """Тест модификации слова 'регион' (винительный падеж) для числа 1"""
    assert modification__region__accusative_case(1) == 'регион'


@pytest.mark.unit
def test_modification__region__accusative_case_2() -> None:
    """Тест модификации слова 'регион' (винительный падеж) для числа 2"""
    assert modification__region__accusative_case(2) == 'региона'


@pytest.mark.unit
def test_modification__region__accusative_case_5() -> None:
    """Тест модификации слова 'регион' (винительный падеж) для числа 5"""
    assert modification__region__accusative_case(5) == 'регионов'


@pytest.mark.unit
def test_modification__region__accusative_case_11() -> None:
    """Тест модификации слова 'регион' (винительный падеж) для числа 11"""
    assert modification__region__accusative_case(11) == 'регионов'


@pytest.mark.unit
def test_modification__region__accusative_case_21() -> None:
    """Тест модификации слова 'регион' (винительный падеж) для числа 21"""
    assert modification__region__accusative_case(21) == 'регион'


@pytest.mark.unit
def test_modification__region__accusative_case_0() -> None:
    """Тест модификации слова 'регион' (винительный падеж) для числа 0"""
    assert modification__region__accusative_case(0) == 'регионов'


@pytest.mark.unit
def test_modification__region__prepositional_case_0() -> None:
    """Тест модификации слова 'регион' (предложный падеж) для числа 0"""
    assert modification__region__prepositional_case(0) == 'регионов'


@pytest.mark.unit
def test_modification__region__prepositional_case_1() -> None:
    """Тест модификации слова 'регион' (предложный падеж) для числа 1"""
    assert modification__region__prepositional_case(1) == 'регионе'


@pytest.mark.unit
def test_modification__region__prepositional_case_2() -> None:
    """Тест модификации слова 'регион' (предложный падеж) для числа 2"""
    assert modification__region__prepositional_case(2) == 'регионах'


@pytest.mark.unit
def test_modification__region__prepositional_case_5() -> None:
    """Тест модификации слова 'регион' (предложный падеж) для числа 5"""
    assert modification__region__prepositional_case(5) == 'регионах'


@pytest.mark.unit
def test_modification__region__prepositional_case_11() -> None:
    """Тест модификации слова 'регион' (предложный падеж) для числа 11"""
    assert modification__region__prepositional_case(11) == 'регионах'


@pytest.mark.unit
def test_modification__region__prepositional_case_21() -> None:
    """Тест модификации слова 'регион' (предложный падеж) для числа 21"""
    assert modification__region__prepositional_case(21) == 'регионе'


@pytest.mark.unit
def test_modification__region__prepositional_case_101() -> None:
    """Тест модификации слова 'регион' (предложный падеж) для числа 101"""
    assert modification__region__prepositional_case(101) == 'регионе'


@pytest.mark.unit
def test_modification__region__prepositional_case_102() -> None:
    """Тест модификации слова 'регион' (предложный падеж) для числа 102"""
    assert modification__region__prepositional_case(102) == 'регионах'


@pytest.mark.unit
def test_modification__region__prepositional_case_1000() -> None:
    """Тест модификации слова 'регион' (предложный падеж) для числа 1000"""
    assert modification__region__prepositional_case(1000) == 'регионах'

