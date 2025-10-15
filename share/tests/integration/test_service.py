"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from unittest.mock import Mock
from django.http import Http404

from share.service import ShareService
from share.structs import TypeOfSharedPage


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_check_permissions_user_exists(test_user_with_share_settings: Any) -> None:
    """Тест проверки прав доступа для существующего пользователя"""
    mock_request = Mock()

    service = ShareService(
        mock_request,
        user_id=test_user_with_share_settings.id,
        requested_page='dashboard',
        country_code=None,
    )

    service.check_permissions_and_get_settings()

    assert service.settings is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_check_permissions_user_not_exists(django_user_model: Any) -> None:
    """Тест проверки прав доступа для несуществующего пользователя"""
    mock_request = Mock()

    service = ShareService(
        mock_request, user_id=99999, requested_page='dashboard', country_code=None
    )

    with pytest.raises(Http404):
        service.check_permissions_and_get_settings()


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_check_permissions_all_disabled(
    test_user_without_share_settings: Any,
) -> None:
    """Тест проверки прав доступа когда все опции отключены"""
    from account.models import ShareSettings

    ShareSettings.objects.create(
        user=test_user_without_share_settings,
        can_share_dashboard=False,
        can_share_city_map=False,
        can_share_region_map=False,
    )

    mock_request = Mock()

    service = ShareService(
        mock_request,
        user_id=test_user_without_share_settings.id,
        requested_page='dashboard',
        country_code=None,
    )

    with pytest.raises(Http404):
        service.check_permissions_and_get_settings()


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_determine_displayed_page(test_user_with_share_settings: Any) -> None:
    """Тест определения отображаемой страницы"""
    from account.models import ShareSettings

    mock_request = Mock()

    service = ShareService(
        mock_request,
        user_id=test_user_with_share_settings.id,
        requested_page='dashboard',
        country_code=None,
    )

    settings = ShareSettings.objects.get(user=test_user_with_share_settings)
    service.settings = settings
    result = service.determine_displayed_page()

    assert result == TypeOfSharedPage.dashboard


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_maybe_redirect_when_pages_match() -> None:
    """Тест что редирект не происходит когда запрошенная и отображаемая страницы совпадают"""
    mock_request = Mock()

    service = ShareService(mock_request, user_id=1, requested_page='dashboard', country_code=None)

    service.requested_page = TypeOfSharedPage.dashboard.value
    service.displayed_page = TypeOfSharedPage.dashboard

    result = service.maybe_redirect_to_valid_page()

    assert result is None


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_maybe_redirect_when_pages_differ() -> None:
    """Тест что редирект происходит когда запрошенная и отображаемая страницы различаются"""
    mock_request = Mock()

    service = ShareService(mock_request, user_id=1, requested_page='dashboard', country_code=None)

    service.requested_page = TypeOfSharedPage.dashboard.value
    service.displayed_page = TypeOfSharedPage.city_map

    result = service.maybe_redirect_to_valid_page()

    assert result is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_resolve_country_valid_code(django_user_model: Any) -> None:
    """Тест разрешения страны по валидному коду"""
    from country.models import Country

    country = Country.objects.create(name='Россия', code='RU')

    mock_request = Mock()

    service = ShareService(mock_request, user_id=1, requested_page='region_map', country_code='RU')

    service.displayed_page = TypeOfSharedPage.region_map
    service.resolve_country_if_needed()

    assert service.country == 'Россия'
    assert service.country_id == country.id


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_resolve_country_invalid_code(django_user_model: Any) -> None:
    """Тест разрешения страны по невалидному коду"""
    mock_request = Mock()

    service = ShareService(
        mock_request, user_id=1, requested_page='region_map', country_code='INVALID'
    )

    service.displayed_page = TypeOfSharedPage.region_map

    with pytest.raises(Http404):
        service.resolve_country_if_needed()


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_resolve_country_not_called_for_dashboard(django_user_model: Any) -> None:
    """Тест что resolve_country_if_needed не вызывается для dashboard"""
    mock_request = Mock()

    service = ShareService(mock_request, user_id=1, requested_page='dashboard', country_code=None)

    service.displayed_page = TypeOfSharedPage.dashboard
    service.resolve_country_if_needed()

    # Для dashboard страна не должна разрешаться
    assert service.country is None
    assert service.country_id is None


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_get_template_name_dashboard() -> None:
    """Тест получения имени шаблона для dashboard"""
    mock_request = Mock(spec=['user'])
    mock_request.user = Mock(spec=['id'])
    mock_request.user.id = 1

    service = ShareService(mock_request, user_id=1, requested_page='dashboard', country_code=None)

    service.displayed_page = TypeOfSharedPage.dashboard

    result = service.get_template_name()

    assert result == 'share/dashboard.html'


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_get_template_name_city_map() -> None:
    """Тест получения имени шаблона для city_map"""
    mock_request = Mock(spec=['user'])
    mock_request.user = Mock(spec=['id'])
    mock_request.user.id = 1

    service = ShareService(mock_request, user_id=1, requested_page='city_map', country_code=None)

    service.displayed_page = TypeOfSharedPage.city_map

    result = service.get_template_name()

    assert result == 'share/city_map.html'


@pytest.mark.integration
@pytest.mark.django_db
def test_share_service_get_template_name_region_map() -> None:
    """Тест получения имени шаблона для region_map"""
    mock_request = Mock(spec=['user'])
    mock_request.user = Mock(spec=['id'])
    mock_request.user.id = 1

    service = ShareService(mock_request, user_id=1, requested_page='region_map', country_code='RU')

    service.displayed_page = TypeOfSharedPage.region_map

    result = service.get_template_name()

    assert result == 'share/region_map.html'
