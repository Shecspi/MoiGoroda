"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from datetime import date, timedelta


# Общие фикстуры для всех тестов приложения advertisement


@pytest.fixture
def future_deadline() -> date:
    """Фикстура с будущей датой (через 30 дней)"""
    return date.today() + timedelta(days=30)


@pytest.fixture
def past_deadline() -> date:
    """Фикстура с прошедшей датой (5 дней назад)"""
    return date.today() - timedelta(days=5)


@pytest.fixture
def today_deadline() -> date:
    """Фикстура с сегодняшней датой"""
    return date.today()

