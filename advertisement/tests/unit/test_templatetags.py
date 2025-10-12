"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from unittest.mock import Mock, patch
from datetime import datetime, date, timedelta


@pytest.mark.unit
def test_get_excluded_users_returns_tuple() -> None:
    """Тест что get_excluded_users возвращает tuple"""
    with patch('advertisement.templatetags.excluded_users.AdvertisementException') as mock_model:
        # Настраиваем мок для возврата пустого queryset
        mock_queryset = Mock()
        mock_queryset.values_list.return_value = []
        mock_model.objects.filter.return_value = mock_queryset

        from advertisement.templatetags.excluded_users import get_excluded_users

        result = get_excluded_users()

        assert isinstance(result, tuple)


@pytest.mark.unit
def test_get_excluded_users_filters_by_current_date() -> None:
    """Тест что get_excluded_users фильтрует по текущей дате"""
    with patch('advertisement.templatetags.excluded_users.AdvertisementException') as mock_model:
        with patch('advertisement.templatetags.excluded_users.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            mock_queryset = Mock()
            mock_queryset.values_list.return_value = []
            mock_model.objects.filter.return_value = mock_queryset

            from advertisement.templatetags.excluded_users import get_excluded_users

            get_excluded_users()

            # Проверяем, что фильтр вызван с deadline__gte
            mock_model.objects.filter.assert_called_once_with(deadline__gte=mock_now)


@pytest.mark.unit
def test_get_excluded_users_returns_user_ids() -> None:
    """Тест что get_excluded_users возвращает ID пользователей"""
    with patch('advertisement.templatetags.excluded_users.AdvertisementException') as mock_model:
        # Настраиваем мок для возврата списка ID
        mock_queryset = Mock()
        mock_queryset.values_list.return_value = [1, 2, 3]
        mock_model.objects.filter.return_value = mock_queryset

        from advertisement.templatetags.excluded_users import get_excluded_users

        result = get_excluded_users()

        assert result == (1, 2, 3)
        mock_queryset.values_list.assert_called_once_with('user__id', flat=True)


@pytest.mark.unit
def test_get_excluded_users_returns_empty_tuple_when_no_exceptions() -> None:
    """Тест что get_excluded_users возвращает пустой tuple когда нет исключений"""
    with patch('advertisement.templatetags.excluded_users.AdvertisementException') as mock_model:
        mock_queryset = Mock()
        mock_queryset.values_list.return_value = []
        mock_model.objects.filter.return_value = mock_queryset

        from advertisement.templatetags.excluded_users import get_excluded_users

        result = get_excluded_users()

        assert result == ()
        assert len(result) == 0


@pytest.mark.unit
def test_get_excluded_users_with_multiple_users() -> None:
    """Тест get_excluded_users с несколькими пользователями"""
    with patch('advertisement.templatetags.excluded_users.AdvertisementException') as mock_model:
        mock_queryset = Mock()
        mock_queryset.values_list.return_value = [10, 20, 30, 40, 50]
        mock_model.objects.filter.return_value = mock_queryset

        from advertisement.templatetags.excluded_users import get_excluded_users

        result = get_excluded_users()

        assert result == (10, 20, 30, 40, 50)
        assert len(result) == 5


@pytest.mark.unit
def test_get_excluded_users_template_tag_registered() -> None:
    """Тест что get_excluded_users зарегистрирован как template tag"""
    from advertisement.templatetags.excluded_users import register, get_excluded_users

    # Проверяем, что функция зарегистрирована
    assert hasattr(register, 'tags')
    # get_excluded_users должен быть в зарегистрированных тегах
    assert 'get_excluded_users' in register.tags

