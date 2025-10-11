"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest


@pytest.mark.unit
def test_share_settings_default_values():
    """Тест значений по умолчанию для модели ShareSettings"""
    from account.models import ShareSettings

    # Создаём объект без указания значений boolean полей
    share_settings = ShareSettings()

    # Проверяем значения по умолчанию
    assert share_settings.can_share is False
    assert share_settings.can_share_dashboard is False
    assert share_settings.can_share_city_map is False
    assert share_settings.can_share_region_map is False
    assert share_settings.can_subscribe is False


@pytest.mark.unit
def test_user_consent_default_consent_given():
    """Тест значения по умолчанию для поля consent_given модели UserConsent"""
    from account.models import UserConsent

    # Создаём объект
    user_consent = UserConsent()

    # Проверяем значение по умолчанию
    assert user_consent.consent_given is True


@pytest.mark.unit
def test_share_settings_meta_verbose_name():
    """Тест verbose_name модели ShareSettings"""
    from account.models import ShareSettings

    assert ShareSettings._meta.verbose_name == 'Параметры публикации статистики'
    assert ShareSettings._meta.verbose_name_plural == 'Параметры публикации статистики'


@pytest.mark.unit
def test_share_settings_field_types():
    """Тест типов полей модели ShareSettings"""
    from account.models import ShareSettings
    from django.db import models

    # Проверяем типы полей
    assert isinstance(ShareSettings._meta.get_field('can_share'), models.BooleanField)
    assert isinstance(ShareSettings._meta.get_field('can_share_dashboard'), models.BooleanField)
    assert isinstance(ShareSettings._meta.get_field('can_share_city_map'), models.BooleanField)
    assert isinstance(ShareSettings._meta.get_field('can_share_region_map'), models.BooleanField)
    assert isinstance(ShareSettings._meta.get_field('can_subscribe'), models.BooleanField)
    assert isinstance(ShareSettings._meta.get_field('user'), models.ForeignKey)


@pytest.mark.unit
def test_user_consent_field_types():
    """Тест типов полей модели UserConsent"""
    from account.models import UserConsent
    from django.db import models

    # Проверяем типы полей
    assert isinstance(UserConsent._meta.get_field('user'), models.ForeignKey)
    assert isinstance(UserConsent._meta.get_field('consent_given'), models.BooleanField)
    assert isinstance(UserConsent._meta.get_field('consent_timestamp'), models.DateTimeField)
    assert isinstance(UserConsent._meta.get_field('policy_version'), models.CharField)
    assert isinstance(UserConsent._meta.get_field('ip_address'), models.GenericIPAddressField)
