"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from services.word_modifications.visited import modification__visited


@pytest.mark.unit
def test_modification__visited_1() -> None:
    """Тест модификации слова 'посещён' для числа 1"""
    assert modification__visited(1) == 'посещён'


@pytest.mark.unit
def test_modification__visited_2() -> None:
    """Тест модификации слова 'посещено' для числа 2"""
    assert modification__visited(2) == 'посещено'


@pytest.mark.unit
def test_modification__visited_5() -> None:
    """Тест модификации слова 'посещено' для числа 5"""
    assert modification__visited(5) == 'посещено'


@pytest.mark.unit
def test_modification__visited_10() -> None:
    """Тест модификации слова 'посещено' для числа 10"""
    assert modification__visited(10) == 'посещено'


@pytest.mark.unit
def test_modification__visited_11() -> None:
    """Тест модификации слова 'посещено' для числа 11"""
    assert modification__visited(11) == 'посещено'


@pytest.mark.unit
def test_modification__visited_21() -> None:
    """Тест модификации слова 'посещён' для числа 21"""
    assert modification__visited(21) == 'посещён'


@pytest.mark.unit
def test_modification__visited_22() -> None:
    """Тест модификации слова 'посещено' для числа 22"""
    assert modification__visited(22) == 'посещено'


@pytest.mark.unit
def test_modification__visited_101() -> None:
    """Тест модификации слова 'посещён' для числа 101"""
    assert modification__visited(101) == 'посещён'


@pytest.mark.unit
def test_modification__visited_102() -> None:
    """Тест модификации слова 'посещено' для числа 102"""
    assert modification__visited(102) == 'посещено'


@pytest.mark.unit
def test_modification__visited_111() -> None:
    """Тест модификации слова 'посещено' для числа 111"""
    assert modification__visited(111) == 'посещено'


@pytest.mark.unit
def test_modification__visited_121() -> None:
    """Тест модификации слова 'посещён' для числа 121"""
    assert modification__visited(121) == 'посещён'


@pytest.mark.unit
def test_modification__visited_1001() -> None:
    """Тест модификации слова 'посещён' для числа 1001"""
    assert modification__visited(1001) == 'посещён'


@pytest.mark.unit
def test_modification__visited_0() -> None:
    """Тест модификации слова 'посещено' для числа 0"""
    assert modification__visited(0) == 'посещено'


@pytest.mark.unit
def test_modification__visited_negative() -> None:
    """Тест модификации слова для отрицательных чисел"""
    assert modification__visited(-1) == 'посещён'
    assert modification__visited(-2) == 'посещено'
