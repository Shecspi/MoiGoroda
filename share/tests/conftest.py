"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any


# Общие фикстуры для всех тестов приложения share


@pytest.fixture
def test_user_with_share_settings(django_user_model: Any) -> Any:
    """Фикстура с пользователем и настройками публикации"""
    from account.models import ShareSettings

    user = django_user_model.objects.create_user(username='testuser', password='password123')
    ShareSettings.objects.create(
        user=user,
        can_share=True,
        can_share_dashboard=True,
        can_share_city_map=True,
        can_share_region_map=True,
        can_subscribe=True,
    )
    return user


@pytest.fixture
def test_user_without_share_settings(django_user_model: Any) -> Any:
    """Фикстура с пользователем без настроек публикации"""
    user = django_user_model.objects.create_user(username='testuser2', password='password123')
    return user
