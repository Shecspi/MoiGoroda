"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from services.word_modifications.city import modification__city


@pytest.mark.unit
def test_modification__city_1() -> None:
    """Тест модификации слова 'город' для числа 1"""
    assert modification__city(1) == 'город'


@pytest.mark.unit
def test_modification__city_2() -> None:
    """Тест модификации слова 'город' для числа 2"""
    assert modification__city(2) == 'города'


@pytest.mark.unit
def test_modification__city_3() -> None:
    """Тест модификации слова 'город' для числа 3"""
    assert modification__city(3) == 'города'


@pytest.mark.unit
def test_modification__city_4() -> None:
    """Тест модификации слова 'город' для числа 4"""
    assert modification__city(4) == 'города'


@pytest.mark.unit
def test_modification__city_5() -> None:
    """Тест модификации слова 'город' для числа 5"""
    assert modification__city(5) == 'городов'


@pytest.mark.unit
def test_modification__city_10() -> None:
    """Тест модификации слова 'город' для числа 10"""
    assert modification__city(10) == 'городов'


@pytest.mark.unit
def test_modification__city_11() -> None:
    """Тест модификации слова 'город' для числа 11"""
    assert modification__city(11) == 'городов'


@pytest.mark.unit
def test_modification__city_20() -> None:
    """Тест модификации слова 'город' для числа 20"""
    assert modification__city(20) == 'городов'


@pytest.mark.unit
def test_modification__city_21() -> None:
    """Тест модификации слова 'город' для числа 21"""
    assert modification__city(21) == 'город'


@pytest.mark.unit
def test_modification__city_22() -> None:
    """Тест модификации слова 'город' для числа 22"""
    assert modification__city(22) == 'города'


@pytest.mark.unit
def test_modification__city_25() -> None:
    """Тест модификации слова 'город' для числа 25"""
    assert modification__city(25) == 'городов'


@pytest.mark.unit
def test_modification__city_100() -> None:
    """Тест модификации слова 'город' для числа 100"""
    assert modification__city(100) == 'городов'


@pytest.mark.unit
def test_modification__city_101() -> None:
    """Тест модификации слова 'город' для числа 101"""
    assert modification__city(101) == 'город'


@pytest.mark.unit
def test_modification__city_102() -> None:
    """Тест модификации слова 'город' для числа 102"""
    assert modification__city(102) == 'города'


@pytest.mark.unit
def test_modification__city_105() -> None:
    """Тест модификации слова 'город' для числа 105"""
    assert modification__city(105) == 'городов'


@pytest.mark.unit
def test_modification__city_111() -> None:
    """Тест модификации слова 'город' для числа 111"""
    assert modification__city(111) == 'городов'


@pytest.mark.unit
def test_modification__city_112() -> None:
    """Тест модификации слова 'город' для числа 112"""
    assert modification__city(112) == 'городов'


@pytest.mark.unit
def test_modification__city_121() -> None:
    """Тест модификации слова 'город' для числа 121"""
    assert modification__city(121) == 'город'


@pytest.mark.unit
def test_modification__city_1000() -> None:
    """Тест модификации слова 'город' для числа 1000"""
    assert modification__city(1000) == 'городов'


@pytest.mark.unit
def test_modification__city_1001() -> None:
    """Тест модификации слова 'город' для числа 1001"""
    assert modification__city(1001) == 'город'


@pytest.mark.unit
def test_modification__city_1002() -> None:
    """Тест модификации слова 'город' для числа 1002"""
    assert modification__city(1002) == 'города'


@pytest.mark.unit
def test_modification__city_1005() -> None:
    """Тест модификации слова 'город' для числа 1005"""
    assert modification__city(1005) == 'городов'


@pytest.mark.unit
def test_modification__city_0() -> None:
    """Тест модификации слова 'город' для числа 0"""
    assert modification__city(0) == 'городов'


@pytest.mark.unit
def test_modification__city_negative() -> None:
    """Тест модификации слова 'город' для отрицательных чисел"""
    # Функция не обрабатывает отрицательные числа специально
    assert modification__city(-1) == 'город'
    assert modification__city(-5) == 'городов'
