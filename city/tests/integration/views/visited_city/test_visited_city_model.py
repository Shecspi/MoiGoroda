"""
Тесты для модели VisitedCity.

Покрывает:
- Структуру модели и мета-данные
- Поля модели и их атрибуты
- Методы модели
- Валидацию данных
- Ограничения базы данных
- Функциональное тестирование

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import date

import pytest
from django import core
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from unittest.mock import MagicMock, patch

from city.models import VisitedCity, City
from country.models import Country


# Тесты структуры модели


@pytest.mark.integration
def test_visited_city_can_create_model_instance() -> None:
    """Проверяет, что можно создать экземпляр модели VisitedCity."""
    assert VisitedCity()


@pytest.mark.integration
def test_visited_city_has_valid_verbose_name() -> None:
    """Проверяет корректные verbose_name и verbose_name_plural."""
    assert VisitedCity._meta.verbose_name == 'Посещённый город'
    assert VisitedCity._meta.verbose_name_plural == 'Посещённые города'


@pytest.mark.integration
def test_visited_city_has_correct_ordering() -> None:
    """Проверяет корректную сортировку модели."""
    assert VisitedCity._meta.ordering == ['-id']


@pytest.mark.integration
def test_visited_city_has_correct_unique_together() -> None:
    """Проверяет корректное ограничение unique_together."""
    unique_together = list(VisitedCity._meta.unique_together)
    assert len(unique_together) == 1
    assert unique_together[0] == ('user', 'city', 'date_of_visit')  # type: ignore[comparison-overlap]


# Тесты полей модели


@pytest.mark.integration
def test_visited_city_has_field_user() -> None:
    """Проверяет поле user модели VisitedCity."""
    field = VisitedCity._meta.get_field('user')

    assert field.verbose_name == 'Пользователь'
    assert field.blank is False
    assert field.null is False
    assert field.remote_field.on_delete == models.CASCADE
    assert isinstance(field, models.ForeignKey)
    assert isinstance(field.remote_field.model(), User)


@pytest.mark.integration
def test_visited_city_has_field_city() -> None:
    """Проверяет поле city модели VisitedCity."""
    field = VisitedCity._meta.get_field('city')

    assert field.verbose_name == 'Город'
    assert field.blank is False
    assert field.null is False
    assert field.remote_field.on_delete == models.CASCADE
    assert isinstance(field, models.ForeignKey)
    assert isinstance(field.remote_field.model(), City)


@pytest.mark.integration
def test_visited_city_has_field_date_of_visit() -> None:
    """Проверяет поле date_of_visit модели VisitedCity."""
    field = VisitedCity._meta.get_field('date_of_visit')

    assert field.verbose_name == 'Дата посещения'
    assert field.blank is True
    assert field.null is True
    assert isinstance(field, models.DateField)


@pytest.mark.integration
def test_visited_city_has_field_has_magnet() -> None:
    """Проверяет поле has_magnet модели VisitedCity."""
    field = VisitedCity._meta.get_field('has_magnet')

    assert field.verbose_name == 'Наличие сувенира из города'
    assert field.blank is True
    assert field.null is False
    assert isinstance(field, models.BooleanField)
    assert field.default is False


@pytest.mark.integration
def test_visited_city_has_field_impression() -> None:
    """Проверяет поле impression модели VisitedCity."""
    field = VisitedCity._meta.get_field('impression')

    assert field.verbose_name == 'Впечатления о городе'
    assert field.blank is True
    assert field.null is True
    assert isinstance(field, models.TextField)


@pytest.mark.integration
def test_visited_city_has_field_rating() -> None:
    """Проверяет поле rating модели VisitedCity."""
    field = VisitedCity._meta.get_field('rating')

    assert field.verbose_name == 'Рейтинг'
    assert field.blank is False
    assert field.null is False
    assert isinstance(field, models.SmallIntegerField)
    assert any(
        isinstance(validator, core.validators.MinValueValidator) and validator.limit_value == 1
        for validator in field.validators
    )
    assert any(
        isinstance(validator, core.validators.MaxValueValidator) and validator.limit_value == 5
        for validator in field.validators
    )


@pytest.mark.integration
def test_visited_city_has_field_is_first_visit() -> None:
    """Проверяет поле is_first_visit модели VisitedCity."""
    field = VisitedCity._meta.get_field('is_first_visit')

    assert field.verbose_name == 'Первый раз в городе?'
    assert field.blank is True
    assert field.null is True
    assert isinstance(field, models.BooleanField)
    assert field.default is True


# Тесты дополнительных атрибутов полей


@pytest.mark.integration
def test_visited_city_has_help_texts() -> None:
    """Проверяет наличие help_text для всех полей."""
    city_field = VisitedCity._meta.get_field('city')
    date_field = VisitedCity._meta.get_field('date_of_visit')
    magnet_field = VisitedCity._meta.get_field('has_magnet')
    impression_field = VisitedCity._meta.get_field('impression')
    rating_field = VisitedCity._meta.get_field('rating')

    assert city_field.help_text == 'Выберите город, который посетили.'
    assert 'ДД.ММ.ГГГГ' in date_field.help_text
    assert 'сувенир' in magnet_field.help_text
    assert 'Markdown' in impression_field.help_text
    assert '1 - плохо, 5 - отлично' in rating_field.help_text


@pytest.mark.integration
def test_visited_city_has_related_name() -> None:
    """Проверяет related_name для поля city."""
    city_field = VisitedCity._meta.get_field('city')
    assert city_field.remote_field.related_name == 'visitedcity'


@pytest.mark.integration
def test_visited_city_has_db_indexes() -> None:
    """Проверяет наличие db_index для соответствующих полей."""
    date_field = VisitedCity._meta.get_field('date_of_visit')
    rating_field = VisitedCity._meta.get_field('rating')
    is_first_visit_field = VisitedCity._meta.get_field('is_first_visit')

    assert date_field.db_index is True  # type: ignore[attr-defined]
    assert rating_field.db_index is True  # type: ignore[attr-defined]
    assert is_first_visit_field.db_index is True  # type: ignore[attr-defined]


# Тесты методов модели


@pytest.mark.integration
def test_visited_city_str_method() -> None:
    """Проверяет метод __str__ модели."""
    visited_city = VisitedCity()
    # Создаем реальный объект City для тестирования
    country = Country(name='Test Country', code='TC')
    city = City(
        title='Test City', country=country, coordinate_width=55.7558, coordinate_longitude=37.6173
    )
    visited_city.city = city
    assert str(visited_city) == 'Test City'


@pytest.mark.integration
def test_visited_city_get_absolute_url() -> None:
    """Проверяет метод get_absolute_url модели."""
    visited_city = VisitedCity()
    visited_city.pk = 1
    expected_url = reverse('city-selected', kwargs={'pk': 1})
    assert visited_city.get_absolute_url() == expected_url


# Функциональные тесты


@pytest.fixture
@pytest.mark.django_db
@pytest.mark.integration
def test_user() -> User:
    """Фикстура для создания тестового пользователя."""
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
@pytest.mark.django_db
@pytest.mark.integration
def test_country() -> Country:
    """Фикстура для создания тестовой страны."""
    return Country.objects.create(name='Test Country', code='TC')


@pytest.fixture
@pytest.mark.django_db
@pytest.mark.integration
def test_city(test_country: Country) -> City:
    """Фикстура для создания тестового города."""
    return City.objects.create(
        title='Test City',
        country=test_country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )


@pytest.mark.django_db
@patch('city.signals.notify_subscribers_on_city_add')
@pytest.mark.integration
def test_visited_city_can_create_instance(
    mock_signal: MagicMock, test_user: User, test_city: City
) -> None:
    """Проверяет создание экземпляра VisitedCity."""
    visited_city = VisitedCity.objects.create(
        user=test_user,
        city=test_city,
        date_of_visit=date(2024, 1, 15),
        rating=5,
        has_magnet=True,
        impression='Great city!',
        is_first_visit=True,
    )

    assert visited_city.user == test_user
    assert visited_city.city == test_city
    assert visited_city.date_of_visit == date(2024, 1, 15)
    assert visited_city.rating == 5
    assert visited_city.has_magnet is True
    assert visited_city.impression == 'Great city!'
    assert visited_city.is_first_visit is True


@pytest.mark.django_db
@patch('city.signals.notify_subscribers_on_city_add')
@pytest.mark.integration
def test_visited_city_rating_validation_min_value(
    mock_signal: MagicMock, test_user: User, test_city: City
) -> None:
    """Проверяет валидацию минимального значения рейтинга."""
    visited_city = VisitedCity(
        user=test_user,
        city=test_city,
        rating=0,  # Меньше минимального значения
    )

    with pytest.raises(ValidationError):
        visited_city.full_clean()


@pytest.mark.django_db
@patch('city.signals.notify_subscribers_on_city_add')
@pytest.mark.integration
def test_visited_city_rating_validation_max_value(
    mock_signal: MagicMock, test_user: User, test_city: City
) -> None:
    """Проверяет валидацию максимального значения рейтинга."""
    visited_city = VisitedCity(
        user=test_user,
        city=test_city,
        rating=6,  # Больше максимального значения
    )

    with pytest.raises(ValidationError):
        visited_city.full_clean()


@pytest.mark.django_db
@patch('city.signals.notify_subscribers_on_city_add')
@pytest.mark.integration
def test_visited_city_rating_validation_valid_values(
    mock_signal: MagicMock, test_user: User, test_city: City
) -> None:
    """Проверяет, что валидные значения рейтинга проходят валидацию."""
    for rating in [1, 2, 3, 4, 5]:
        visited_city = VisitedCity(user=test_user, city=test_city, rating=rating)
        # Не должно вызывать исключение
        visited_city.full_clean()


@pytest.mark.django_db
@patch('city.signals.notify_subscribers_on_city_add')
@pytest.mark.integration
def test_visited_city_unique_together_constraint(
    mock_signal: MagicMock, test_user: User, test_city: City
) -> None:
    """Проверяет ограничение unique_together."""
    # Создаем первый экземпляр
    VisitedCity.objects.create(
        user=test_user, city=test_city, date_of_visit=date(2024, 1, 15), rating=5
    )

    # Пытаемся создать второй экземпляр с теми же user, city, date_of_visit
    with pytest.raises(Exception):  # IntegrityError или ValidationError
        VisitedCity.objects.create(
            user=test_user, city=test_city, date_of_visit=date(2024, 1, 15), rating=3
        )


@pytest.mark.django_db
@patch('city.signals.notify_subscribers_on_city_add')
@pytest.mark.integration
def test_visited_city_default_values(
    mock_signal: MagicMock, test_user: User, test_city: City
) -> None:
    """Проверяет значения по умолчанию."""
    visited_city = VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

    assert visited_city.has_magnet is False  # default=False
    assert visited_city.is_first_visit is True  # default=True
