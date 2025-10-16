"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from unittest.mock import Mock

from share.service import get_displayed_page, ShareService
from share.structs import TypeOfSharedPage


# ===== Тесты для get_displayed_page =====


@pytest.mark.unit
def test_get_displayed_page_requested_dashboard_available() -> None:
    """Тест что запрошенная dashboard возвращается если доступна"""
    from account.models import ShareSettings

    settings = ShareSettings(
        can_share_dashboard=True, can_share_city_map=False, can_share_region_map=False
    )

    result = get_displayed_page('dashboard', settings)

    assert result == TypeOfSharedPage.dashboard


@pytest.mark.unit
def test_get_displayed_page_requested_city_map_available() -> None:
    """Тест что запрошенная city_map возвращается если доступна"""
    from account.models import ShareSettings

    settings = ShareSettings(
        can_share_dashboard=False, can_share_city_map=True, can_share_region_map=False
    )

    result = get_displayed_page('city_map', settings)

    assert result == TypeOfSharedPage.city_map


@pytest.mark.unit
def test_get_displayed_page_requested_region_map_available() -> None:
    """Тест что запрошенная region_map возвращается если доступна"""
    from account.models import ShareSettings

    settings = ShareSettings(
        can_share_dashboard=False, can_share_city_map=False, can_share_region_map=True
    )

    result = get_displayed_page('region_map', settings)

    assert result == TypeOfSharedPage.region_map


@pytest.mark.unit
def test_get_displayed_page_fallback_to_alternative() -> None:
    """Тест что при недоступности запрошенной страницы возвращается альтернатива"""
    from account.models import ShareSettings

    settings = ShareSettings(
        can_share_dashboard=False, can_share_city_map=True, can_share_region_map=False
    )

    result = get_displayed_page('dashboard', settings)

    assert result == TypeOfSharedPage.city_map


@pytest.mark.unit
def test_get_displayed_page_no_requested_page() -> None:
    """Тест что при отсутствии запроса возвращается первая доступная страница"""
    from account.models import ShareSettings

    settings = ShareSettings(
        can_share_dashboard=False, can_share_city_map=True, can_share_region_map=False
    )

    result = get_displayed_page(None, settings)

    assert result == TypeOfSharedPage.city_map


@pytest.mark.unit
def test_get_displayed_page_no_available_pages() -> None:
    """Тест что при отсутствии доступных страниц возвращается None"""
    from account.models import ShareSettings

    settings = ShareSettings(
        can_share_dashboard=False, can_share_city_map=False, can_share_region_map=False
    )

    result = get_displayed_page('dashboard', settings)

    assert result is None


@pytest.mark.unit
def test_get_displayed_page_invalid_requested_page() -> None:
    """Тест что при невалидном запросе возвращается первая доступная страница"""
    from account.models import ShareSettings

    settings = ShareSettings(
        can_share_dashboard=True, can_share_city_map=False, can_share_region_map=False
    )

    result = get_displayed_page('invalid_page', settings)

    # Так как invalid_page не валиден, функция возвращает первую доступную страницу
    assert result == TypeOfSharedPage.dashboard


@pytest.mark.unit
def test_get_displayed_page_priority_dashboard() -> None:
    """Тест приоритета для dashboard"""
    from account.models import ShareSettings

    settings = ShareSettings(
        can_share_dashboard=True, can_share_city_map=True, can_share_region_map=True
    )

    result = get_displayed_page('dashboard', settings)

    # Dashboard имеет высший приоритет при запросе dashboard
    assert result == TypeOfSharedPage.dashboard


@pytest.mark.unit
def test_get_displayed_page_priority_city_map() -> None:
    """Тест приоритета для city_map"""
    from account.models import ShareSettings

    settings = ShareSettings(
        can_share_dashboard=True, can_share_city_map=True, can_share_region_map=True
    )

    result = get_displayed_page('city_map', settings)

    # city_map имеет высший приоритет при запросе city_map
    assert result == TypeOfSharedPage.city_map


@pytest.mark.unit
def test_get_displayed_page_priority_region_map() -> None:
    """Тест приоритета для region_map"""
    from account.models import ShareSettings

    settings = ShareSettings(
        can_share_dashboard=True, can_share_city_map=True, can_share_region_map=True
    )

    result = get_displayed_page('region_map', settings)

    # region_map имеет высший приоритет при запросе region_map
    assert result == TypeOfSharedPage.region_map


# ===== Тесты для ShareService =====


@pytest.mark.unit
def test_share_service_init() -> None:
    """Тест инициализации ShareService"""
    mock_request = Mock()

    service = ShareService(mock_request, user_id=1, requested_page='dashboard', country_code='RU')

    assert service.request == mock_request
    assert service.user_id == 1
    assert service.requested_page == 'dashboard'
    assert service.country_code == 'RU'
    assert service.displayed_page is None


@pytest.mark.unit
def test_share_service_handle_redirects_for_region_map_without_country() -> None:
    """Тест редиректа для region_map без кода страны"""
    mock_request = Mock()

    service = ShareService(
        mock_request, user_id=1, requested_page=TypeOfSharedPage.region_map, country_code=None
    )

    result = service.handle_redirects_if_needed()

    assert result is not None


@pytest.mark.unit
def test_share_service_handle_redirects_for_region_map_with_country() -> None:
    """Тест отсутствия редиректа для region_map с кодом страны"""
    mock_request = Mock()

    service = ShareService(
        mock_request, user_id=1, requested_page=TypeOfSharedPage.region_map, country_code='RU'
    )

    result = service.handle_redirects_if_needed()

    assert result is None


@pytest.mark.unit
def test_share_service_handle_redirects_for_dashboard() -> None:
    """Тест отсутствия редиректа для dashboard"""
    mock_request = Mock()

    service = ShareService(mock_request, user_id=1, requested_page='dashboard', country_code=None)

    result = service.handle_redirects_if_needed()

    assert result is None
