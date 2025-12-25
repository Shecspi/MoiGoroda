"""
Тесты для модели CityListDefaultSettings.

Покрывает:
- Структуру модели и мета-данные
- Поля модели и их атрибуты
- Методы модели
- Валидацию данных

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.contrib.auth.models import User
from django.db import models, IntegrityError

from city.models import CityListDefaultSettings


# Тесты структуры модели


@pytest.mark.unit
def test_city_list_default_settings_can_create_model_instance() -> None:
    """Проверяет, что можно создать экземпляр модели CityListDefaultSettings."""
    assert CityListDefaultSettings()


@pytest.mark.unit
def test_city_list_default_settings_has_valid_verbose_name() -> None:
    """Проверяет корректные verbose_name и verbose_name_plural."""
    assert CityListDefaultSettings._meta.verbose_name == 'Настройка по умолчанию списка городов'
    assert (
        CityListDefaultSettings._meta.verbose_name_plural == 'Настройки по умолчанию списка городов'
    )


@pytest.mark.unit
def test_city_list_default_settings_has_correct_ordering() -> None:
    """Проверяет корректную сортировку модели."""
    assert CityListDefaultSettings._meta.ordering == ['user', 'parameter_type']


@pytest.mark.unit
def test_city_list_default_settings_has_unique_together() -> None:
    """Проверяет наличие unique_together для user и parameter_type."""
    unique_together = CityListDefaultSettings._meta.unique_together
    assert ('user', 'parameter_type') in unique_together


# Тесты полей модели


@pytest.mark.unit
def test_city_list_default_settings_has_field_user() -> None:
    """Проверяет поле user модели CityListDefaultSettings."""
    field = CityListDefaultSettings._meta.get_field('user')

    assert field.verbose_name == 'Пользователь'
    assert field.blank is False
    assert field.null is False
    assert field.remote_field.on_delete == models.CASCADE
    assert isinstance(field, models.ForeignKey)
    assert isinstance(field.remote_field.model(), User)


@pytest.mark.unit
def test_city_list_default_settings_has_field_parameter_type() -> None:
    """Проверяет поле parameter_type модели CityListDefaultSettings."""
    field = CityListDefaultSettings._meta.get_field('parameter_type')

    assert field.verbose_name == 'Тип параметра'
    assert field.blank is False
    assert field.null is False
    assert field.max_length == 10
    assert isinstance(field, models.CharField)
    assert field.choices is not None
    choices_list = list(field.choices) if field.choices else []
    assert len(choices_list) == 2
    assert ('filter', 'Фильтрация') in choices_list
    assert ('sort', 'Сортировка') in choices_list


@pytest.mark.unit
def test_city_list_default_settings_has_field_parameter_value() -> None:
    """Проверяет поле parameter_value модели CityListDefaultSettings."""
    field = CityListDefaultSettings._meta.get_field('parameter_value')

    assert field.verbose_name == 'Значение параметра'
    assert field.blank is False
    assert field.null is False
    assert field.max_length == 50
    assert isinstance(field, models.CharField)


# Тесты методов модели


@pytest.mark.unit
@pytest.mark.django_db
def test_city_list_default_settings_str_method(django_user_model: type[User]) -> None:
    """Проверяет метод __str__ модели."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    settings = CityListDefaultSettings(
        user=user,
        parameter_type='filter',
        parameter_value='no_filter',
    )
    settings.save()
    assert 'Фильтрация' in str(settings)
    assert 'testuser' in str(settings)
    assert 'no_filter' in str(settings)


@pytest.mark.unit
@pytest.mark.django_db
def test_city_list_default_settings_get_parameter_type_display(
    django_user_model: type[User],
) -> None:
    """Проверяет метод get_parameter_type_display."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    settings_filter = CityListDefaultSettings(
        user=user,
        parameter_type='filter',
        parameter_value='no_filter',
    )
    assert settings_filter.get_parameter_type_display() == 'Фильтрация'

    settings_sort = CityListDefaultSettings(
        user=user,
        parameter_type='sort',
        parameter_value='name_down',
    )
    assert settings_sort.get_parameter_type_display() == 'Сортировка'


# Функциональные тесты


@pytest.mark.unit
@pytest.mark.django_db
def test_city_list_default_settings_can_create_filter_setting(
    django_user_model: type[User],
) -> None:
    """Проверяет создание настройки фильтрации."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    settings = CityListDefaultSettings.objects.create(
        user=user,
        parameter_type='filter',
        parameter_value='no_magnet',
    )

    assert settings.user == user
    assert settings.parameter_type == 'filter'
    assert settings.parameter_value == 'no_magnet'


@pytest.mark.unit
@pytest.mark.django_db
def test_city_list_default_settings_can_create_sort_setting(django_user_model: type[User]) -> None:
    """Проверяет создание настройки сортировки."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    settings = CityListDefaultSettings.objects.create(
        user=user,
        parameter_type='sort',
        parameter_value='name_down',
    )

    assert settings.user == user
    assert settings.parameter_type == 'sort'
    assert settings.parameter_value == 'name_down'


@pytest.mark.unit
@pytest.mark.django_db
def test_city_list_default_settings_unique_together_constraint(
    django_user_model: type[User],
) -> None:
    """Проверяет ограничение unique_together для user и parameter_type."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    CityListDefaultSettings.objects.create(
        user=user,
        parameter_type='filter',
        parameter_value='no_filter',
    )

    # Попытка создать вторую запись с тем же user и parameter_type должна вызвать ошибку
    with pytest.raises(IntegrityError):
        CityListDefaultSettings.objects.create(
            user=user,
            parameter_type='filter',
            parameter_value='magnet',
        )


@pytest.mark.unit
@pytest.mark.django_db
def test_city_list_default_settings_can_have_both_filter_and_sort(
    django_user_model: type[User],
) -> None:
    """Проверяет, что пользователь может иметь и фильтр, и сортировку."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    filter_settings = CityListDefaultSettings.objects.create(
        user=user,
        parameter_type='filter',
        parameter_value='no_filter',
    )
    sort_settings = CityListDefaultSettings.objects.create(
        user=user,
        parameter_type='sort',
        parameter_value='name_down',
    )

    assert filter_settings.parameter_type == 'filter'
    assert sort_settings.parameter_type == 'sort'
    assert CityListDefaultSettings.objects.filter(user=user).count() == 2


@pytest.mark.unit
@pytest.mark.django_db
def test_city_list_default_settings_ordering(django_user_model: type[User]) -> None:
    """Проверяет сортировку настроек по user и parameter_type."""
    user1 = django_user_model.objects.create_user(username='user1', password='pass')
    user2 = django_user_model.objects.create_user(username='user2', password='pass')

    # Создаём настройки в разном порядке
    CityListDefaultSettings.objects.create(
        user=user2, parameter_type='sort', parameter_value='name_down'
    )
    CityListDefaultSettings.objects.create(
        user=user1, parameter_type='sort', parameter_value='name_up'
    )
    CityListDefaultSettings.objects.create(
        user=user1, parameter_type='filter', parameter_value='no_filter'
    )

    settings = list(CityListDefaultSettings.objects.all())
    assert settings[0].user == user1
    assert settings[0].parameter_type == 'filter'
    assert settings[1].user == user1
    assert settings[1].parameter_type == 'sort'
    assert settings[2].user == user2
    assert settings[2].parameter_type == 'sort'
