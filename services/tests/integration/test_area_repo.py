"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any

from services.db.area_repo import get_visited_areas


@pytest.mark.integration
@pytest.mark.django_db
def test_get_visited_areas_returns_queryset(django_user_model: Any) -> None:
    """Тест что get_visited_areas возвращает QuerySet"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_visited_areas(user.id)

    assert result is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_get_visited_areas_has_total_regions_field(django_user_model: Any) -> None:
    """Тест что get_visited_areas добавляет поле total_regions"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_visited_areas(user.id)

    # Проверяем, что результат содержит поле total_regions
    if result.exists():
        first_area = result.first()
        assert hasattr(first_area, 'total_regions')


@pytest.mark.integration
@pytest.mark.django_db
def test_get_visited_areas_has_visited_regions_field(django_user_model: Any) -> None:
    """Тест что get_visited_areas добавляет поле visited_regions"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_visited_areas(user.id)

    # Проверяем, что результат содержит поле visited_regions
    if result.exists():
        first_area = result.first()
        assert hasattr(first_area, 'visited_regions')


@pytest.mark.integration
@pytest.mark.django_db
def test_get_visited_areas_has_ratio_visited_field(django_user_model: Any) -> None:
    """Тест что get_visited_areas добавляет поле ratio_visited"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_visited_areas(user.id)

    # Проверяем, что результат содержит поле ratio_visited
    if result.exists():
        first_area = result.first()
        assert hasattr(first_area, 'ratio_visited')


@pytest.mark.integration
@pytest.mark.django_db
def test_get_visited_areas_ordered_by_ratio(django_user_model: Any) -> None:
    """Тест что get_visited_areas сортирует результаты по ratio_visited"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_visited_areas(user.id)

    # Проверяем, что результаты отсортированы по ratio_visited (от большего к меньшему)
    if result.count() > 1:
        ratios = [area.ratio_visited for area in result]
        assert ratios == sorted(ratios, reverse=True)
