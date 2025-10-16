"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from services.calculate import calculate_ratio


# ===== Тесты для calculate_ratio =====


@pytest.mark.unit
def test_calculate_ratio_normal_case() -> None:
    """Тест расчёта процентного соотношения для нормального случая"""
    result = calculate_ratio(50, 100)
    assert result == 50


@pytest.mark.unit
def test_calculate_ratio_100_percent() -> None:
    """Тест расчёта 100% соотношения"""
    result = calculate_ratio(100, 100)
    assert result == 100


@pytest.mark.unit
def test_calculate_ratio_0_percent() -> None:
    """Тест расчёта 0% соотношения"""
    result = calculate_ratio(0, 100)
    assert result == 0


@pytest.mark.unit
def test_calculate_ratio_zero_divisor() -> None:
    """Тест расчёта при нулевом делителе"""
    result = calculate_ratio(50, 0)
    assert result == 0


@pytest.mark.unit
def test_calculate_ratio_both_zero() -> None:
    """Тест расчёта при нулевых значениях"""
    result = calculate_ratio(0, 0)
    assert result == 0


@pytest.mark.unit
def test_calculate_ratio_rounding_down() -> None:
    """Тест округления вниз"""
    result = calculate_ratio(1, 3)
    assert result == 33  # 33.33... округляется до 33


@pytest.mark.unit
def test_calculate_ratio_rounding_up() -> None:
    """Тест округления вверх"""
    result = calculate_ratio(2, 3)
    assert result == 66  # 66.66... округляется до 66


@pytest.mark.unit
def test_calculate_ratio_large_numbers() -> None:
    """Тест расчёта для больших чисел"""
    result = calculate_ratio(75000, 100000)
    assert result == 75


@pytest.mark.unit
def test_calculate_ratio_small_numbers() -> None:
    """Тест расчёта для малых чисел"""
    result = calculate_ratio(1, 1000)
    assert result == 0  # 0.1% округляется до 0


@pytest.mark.unit
def test_calculate_ratio_one_percent() -> None:
    """Тест расчёта 1%"""
    result = calculate_ratio(1, 100)
    assert result == 1


@pytest.mark.unit
def test_calculate_ratio_99_percent() -> None:
    """Тест расчёта 99%"""
    result = calculate_ratio(99, 100)
    assert result == 99


@pytest.mark.unit
def test_calculate_ratio_negative_divisible() -> None:
    """Тест расчёта с отрицательным делимым"""
    result = calculate_ratio(-50, 100)
    assert result == -50


@pytest.mark.unit
def test_calculate_ratio_negative_divisor() -> None:
    """Тест расчёта с отрицательным делителем"""
    result = calculate_ratio(50, -100)
    assert result == -50


@pytest.mark.unit
def test_calculate_ratio_both_negative() -> None:
    """Тест расчёта с отрицательными значениями"""
    result = calculate_ratio(-50, -100)
    assert result == 50


@pytest.mark.unit
def test_calculate_ratio_returns_integer() -> None:
    """Тест что функция возвращает целое число"""
    result = calculate_ratio(33, 100)
    assert isinstance(result, int)


@pytest.mark.unit
def test_calculate_ratio_precision() -> None:
    """Тест точности расчёта"""
    result = calculate_ratio(1, 3)
    # Результат должен быть округлён до целого
    assert result in [33, 34]  # Зависит от реализации округления
