"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from datetime import date, timedelta
from unittest.mock import Mock
from django.contrib.admin.sites import AdminSite

from advertisement.models import AdvertisementException
from advertisement.admin import AdvertisementExceptionAdmin


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_admin_registered() -> None:
    """Тест что AdvertisementExceptionAdmin зарегистрирован в admin"""
    from django.contrib import admin

    assert AdvertisementException in admin.site._registry
    assert isinstance(admin.site._registry[AdvertisementException], AdvertisementExceptionAdmin)


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_admin_list_display() -> None:
    """Тест list_display в AdvertisementExceptionAdmin"""
    admin_instance = AdvertisementExceptionAdmin(AdvertisementException, AdminSite())

    assert admin_instance.list_display == ('user', 'deadline')


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_admin_search_fields() -> None:
    """Тест search_fields в AdvertisementExceptionAdmin"""
    admin_instance = AdvertisementExceptionAdmin(AdvertisementException, AdminSite())

    assert admin_instance.search_fields == ('user',)


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_admin_has_permissions(django_user_model: Any) -> None:
    """Тест что AdvertisementExceptionAdmin имеет стандартные permissions"""
    admin_instance = AdvertisementExceptionAdmin(AdvertisementException, AdminSite())

    # Проверяем, что методы существуют
    assert hasattr(admin_instance, 'has_add_permission')
    assert hasattr(admin_instance, 'has_change_permission')
    assert hasattr(admin_instance, 'has_delete_permission')
    assert callable(admin_instance.has_add_permission)
    assert callable(admin_instance.has_change_permission)
    assert callable(admin_instance.has_delete_permission)


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_admin_queryset(django_user_model: Any) -> None:
    """Тест что admin queryset возвращает все исключения"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    deadline = date.today() + timedelta(days=30)
    AdvertisementException.objects.create(user=user1, deadline=deadline)
    AdvertisementException.objects.create(user=user2, deadline=deadline)

    admin_instance = AdvertisementExceptionAdmin(AdvertisementException, AdminSite())
    request = Mock()

    queryset = admin_instance.get_queryset(request)

    assert queryset.count() == 2


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_admin_display_user_field(django_user_model: Any) -> None:
    """Тест отображения поля user в админке"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    deadline = date.today() + timedelta(days=30)

    exception = AdvertisementException.objects.create(user=user, deadline=deadline)

    # Проверяем, что user корректно отображается
    assert str(exception.user) == 'testuser'


@pytest.mark.integration
@pytest.mark.django_db
def test_advertisement_exception_admin_display_deadline_field(django_user_model: Any) -> None:
    """Тест отображения поля deadline в админке"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    deadline = date(2024, 12, 31)

    exception = AdvertisementException.objects.create(user=user, deadline=deadline)

    assert exception.deadline == date(2024, 12, 31)
