"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any


@pytest.mark.unit
def test_advertisement_exception_meta_verbose_name() -> None:
    """Тест verbose_name модели AdvertisementException"""
    from advertisement.models import AdvertisementException

    assert AdvertisementException._meta.verbose_name == 'Исключённый пользователь'
    assert AdvertisementException._meta.verbose_name_plural == 'Исключённые пользователи'


@pytest.mark.unit
def test_advertisement_exception_field_types() -> None:
    """Тест типов полей модели AdvertisementException"""
    from advertisement.models import AdvertisementException
    from django.db import models

    # Проверяем типы полей
    assert isinstance(AdvertisementException._meta.get_field('user'), models.ForeignKey)
    assert isinstance(AdvertisementException._meta.get_field('deadline'), models.DateField)


@pytest.mark.unit
def test_advertisement_exception_field_properties() -> None:
    """Тест свойств полей модели AdvertisementException"""
    from advertisement.models import AdvertisementException

    user_field = AdvertisementException._meta.get_field('user')
    deadline_field = AdvertisementException._meta.get_field('deadline')

    # Проверяем свойства полей
    assert user_field.null is False
    assert deadline_field.null is False
    assert deadline_field.blank is False


@pytest.mark.unit
def test_advertisement_exception_has_required_fields() -> None:
    """Тест наличия всех обязательных полей в модели"""
    from advertisement.models import AdvertisementException

    exception = AdvertisementException()

    # Проверяем наличие полей через _meta
    field_names = [f.name for f in AdvertisementException._meta.get_fields()]
    assert 'user' in field_names
    assert 'deadline' in field_names
    assert 'id' in field_names


@pytest.mark.unit
def test_advertisement_exception_on_delete_cascade() -> None:
    """Тест что при удалении пользователя исключение тоже удаляется (CASCADE)"""
    from advertisement.models import AdvertisementException
    from django.db.models import CASCADE

    user_field = AdvertisementException._meta.get_field('user')
    assert user_field.remote_field.on_delete == CASCADE

