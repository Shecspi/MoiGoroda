"""
Тесты для модели DistrictMapColorSettings.

Покрывает:
- Структуру модели и мета-данные
- Поля модели (user, color_visited, color_not_visited, created_at, updated_at)
- Методы модели (__str__)
- Создание записей с полными и частичными данными
- Изоляцию по пользователю (OneToOne)

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError, models

from city.models import DistrictMapColorSettings


# Тесты структуры модели


@pytest.mark.unit
def test_district_map_color_settings_can_create_model_instance() -> None:
    """Проверяет, что можно создать экземпляр модели (без сохранения)."""
    assert DistrictMapColorSettings()


@pytest.mark.unit
def test_district_map_color_settings_has_valid_verbose_name() -> None:
    """Проверяет корректные verbose_name и verbose_name_plural."""
    assert DistrictMapColorSettings._meta.verbose_name == 'Настройки цветов карты районов'
    assert (
        DistrictMapColorSettings._meta.verbose_name_plural == 'Настройки цветов карты районов'
    )


# Тесты полей модели


@pytest.mark.unit
def test_district_map_color_settings_has_field_user() -> None:
    """Проверяет поле user модели DistrictMapColorSettings."""
    field = DistrictMapColorSettings._meta.get_field('user')

    assert field.verbose_name == 'Пользователь'
    assert field.blank is False
    assert field.null is False
    assert field.remote_field.on_delete == models.CASCADE
    assert isinstance(field, models.OneToOneField)
    assert field.remote_field.related_name == 'district_map_color_settings'


@pytest.mark.unit
def test_district_map_color_settings_has_field_color_visited() -> None:
    """Проверяет поле color_visited — nullable, без default."""
    field = DistrictMapColorSettings._meta.get_field('color_visited')

    assert field.verbose_name == 'Цвет посещённых районов'
    assert field.blank is True
    assert field.null is True
    assert field.max_length == 7
    assert isinstance(field, models.CharField)
    assert 'rrggbb' in (field.help_text or '').lower()


@pytest.mark.unit
def test_district_map_color_settings_has_field_color_not_visited() -> None:
    """Проверяет поле color_not_visited — nullable, без default."""
    field = DistrictMapColorSettings._meta.get_field('color_not_visited')

    assert field.verbose_name == 'Цвет непосещённых районов'
    assert field.blank is True
    assert field.null is True
    assert field.max_length == 7
    assert isinstance(field, models.CharField)


@pytest.mark.unit
def test_district_map_color_settings_has_field_created_at() -> None:
    """Проверяет поле created_at (auto_now_add)."""
    field = DistrictMapColorSettings._meta.get_field('created_at')

    assert field.verbose_name == 'Дата и время создания'
    assert field.auto_now_add is True


@pytest.mark.unit
def test_district_map_color_settings_has_field_updated_at() -> None:
    """Проверяет поле updated_at (auto_now)."""
    field = DistrictMapColorSettings._meta.get_field('updated_at')

    assert field.verbose_name == 'Дата и время изменения'
    assert field.auto_now is True


# Тесты методов модели


@pytest.mark.unit
@pytest.mark.django_db
def test_district_map_color_settings_str_method(django_user_model: type[User]) -> None:
    """Проверяет метод __str__ модели."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    settings = DistrictMapColorSettings.objects.create(
        user=user,
        color_visited='#4fbf4f',
        color_not_visited='#bbbbbb',
    )
    assert 'testuser' in str(settings)
    assert 'Цвета' in str(settings) or 'карты' in str(settings).lower()


# Функциональные тесты


@pytest.mark.unit
@pytest.mark.django_db
def test_district_map_color_settings_create_with_both_colors(
    django_user_model: type[User],
) -> None:
    """Проверяет создание записи с обоими цветами."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    settings = DistrictMapColorSettings.objects.create(
        user=user,
        color_visited='#4fbf4f',
        color_not_visited='#bbbbbb',
    )

    assert settings.user == user
    assert settings.color_visited == '#4fbf4f'
    assert settings.color_not_visited == '#bbbbbb'
    assert settings.created_at is not None
    assert settings.updated_at is not None


@pytest.mark.unit
@pytest.mark.django_db
def test_district_map_color_settings_create_with_only_visited(
    django_user_model: type[User],
) -> None:
    """Проверяет создание записи только с color_visited."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    settings = DistrictMapColorSettings.objects.create(
        user=user,
        color_visited='#ff0000',
        color_not_visited=None,
    )

    assert settings.color_visited == '#ff0000'
    assert settings.color_not_visited is None


@pytest.mark.unit
@pytest.mark.django_db
def test_district_map_color_settings_create_with_only_not_visited(
    django_user_model: type[User],
) -> None:
    """Проверяет создание записи только с color_not_visited."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    settings = DistrictMapColorSettings.objects.create(
        user=user,
        color_visited=None,
        color_not_visited='#00ff00',
    )

    assert settings.color_visited is None
    assert settings.color_not_visited == '#00ff00'


@pytest.mark.unit
@pytest.mark.django_db
def test_district_map_color_settings_one_per_user(django_user_model: type[User]) -> None:
    """Проверяет, что у пользователя может быть только одна запись (OneToOne)."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    DistrictMapColorSettings.objects.create(
        user=user,
        color_visited='#4fbf4f',
        color_not_visited='#bbbbbb',
    )

    with pytest.raises(IntegrityError):
        DistrictMapColorSettings.objects.create(
            user=user,
            color_visited='#ff0000',
            color_not_visited='#00ff00',
        )


@pytest.mark.unit
@pytest.mark.django_db
def test_district_map_color_settings_related_name(django_user_model: type[User]) -> None:
    """Проверяет related_name district_map_color_settings у User."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    DistrictMapColorSettings.objects.create(
        user=user,
        color_visited='#4fbf4f',
        color_not_visited='#bbbbbb',
    )

    assert hasattr(user, 'district_map_color_settings')
    assert user.district_map_color_settings.color_visited == '#4fbf4f'
