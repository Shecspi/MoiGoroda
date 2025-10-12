"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest


@pytest.mark.unit
def test_advertisement_config_name() -> None:
    """Тест имени конфигурации приложения"""
    from advertisement.apps import AdvertisementConfig

    assert AdvertisementConfig.name == 'advertisement'


@pytest.mark.unit
def test_advertisement_config_verbose_name() -> None:
    """Тест verbose_name конфигурации приложения"""
    from advertisement.apps import AdvertisementConfig

    assert AdvertisementConfig.verbose_name == 'Реклама'


@pytest.mark.unit
def test_advertisement_config_default_auto_field() -> None:
    """Тест default_auto_field конфигурации приложения"""
    from advertisement.apps import AdvertisementConfig

    assert AdvertisementConfig.default_auto_field == 'django.db.models.BigAutoField'


@pytest.mark.unit
def test_advertisement_config_inherits_from_app_config() -> None:
    """Тест что AdvertisementConfig наследуется от AppConfig"""
    from advertisement.apps import AdvertisementConfig
    from django.apps import AppConfig

    assert issubclass(AdvertisementConfig, AppConfig)
