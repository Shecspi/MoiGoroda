"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest


# Общие фикстуры для всех тестов приложения account


@pytest.fixture
def api_client():
    """Фикстура для API клиента (если понадобится в будущем)"""
    from rest_framework.test import APIClient

    return APIClient()


# Можно добавить другие общие фикстуры здесь
