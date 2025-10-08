"""
Тесты для модели City.

Покрывает:
- Структуру модели и мета-данные
- Поля модели и их атрибуты
- Методы модели

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.db import models
from django.urls import reverse

from city.models import City
from country.models import Country


# Тесты структуры модели


def test_city_can_create_model_instance() -> None:
    """Проверяет, что можно создать экземпляр модели City."""
    assert City()


def test_city_has_valid_verbose_name() -> None:
    """Проверяет корректные verbose_name и verbose_name_plural."""
    assert City._meta.verbose_name == 'Город'
    assert City._meta.verbose_name_plural == 'Города'


def test_city_has_correct_ordering() -> None:
    """Проверяет корректную сортировку модели."""
    assert City._meta.ordering == ['title']


# Тесты полей модели


def test_city_has_field_title() -> None:
    """Проверяет поле title модели City."""
    field = City._meta.get_field('title')

    assert field.verbose_name == 'Название'
    assert field.blank is False
    assert field.null is False
    assert field.max_length == 100
    assert isinstance(field, models.CharField)


def test_city_has_field_country() -> None:
    """Проверяет поле country модели City."""
    field = City._meta.get_field('country')

    assert field.verbose_name == 'Страна'
    assert field.blank is False
    assert field.null is False
    assert field.remote_field.on_delete == models.PROTECT
    assert isinstance(field, models.ForeignKey)
    assert isinstance(field.remote_field.model(), Country)


def test_city_has_field_region() -> None:
    """Проверяет поле region модели City."""
    field = City._meta.get_field('region')

    assert field.verbose_name == 'Регион'
    assert field.blank is True  # Регион опционален!
    assert field.null is True  # Регион опционален!
    assert field.remote_field.on_delete == models.CASCADE
    assert isinstance(field, models.ForeignKey)


def test_city_has_field_population() -> None:
    """Проверяет поле population модели City."""
    field = City._meta.get_field('population')

    assert field.verbose_name == 'Численность населения'
    assert field.blank is True
    assert field.null is True
    assert isinstance(field, models.PositiveIntegerField)


def test_city_has_field_date_of_foundation() -> None:
    """Проверяет поле date_of_foundation модели City."""
    field = City._meta.get_field('date_of_foundation')

    assert field.verbose_name == 'Год основания'
    assert field.blank is True
    assert field.null is True
    assert isinstance(field, models.PositiveSmallIntegerField)


def test_city_has_field_coordinate_width() -> None:
    """Проверяет поле coordinate_width модели City."""
    field = City._meta.get_field('coordinate_width')

    assert field.verbose_name == 'Широта'
    assert field.blank is False
    assert field.null is False
    assert isinstance(field, models.FloatField)


def test_city_has_field_coordinate_longitude() -> None:
    """Проверяет поле coordinate_longitude модели City."""
    field = City._meta.get_field('coordinate_longitude')

    assert field.verbose_name == 'Долгота'
    assert field.blank is False
    assert field.null is False
    assert isinstance(field, models.FloatField)


def test_city_has_field_wiki() -> None:
    """Проверяет поле wiki модели City."""
    field = City._meta.get_field('wiki')

    assert field.verbose_name == 'Ссылка на Wikipedia'
    assert field.blank is True
    assert field.null is True
    assert field.max_length == 256
    assert isinstance(field, models.URLField)


def test_city_has_field_image() -> None:
    """Проверяет поле image модели City."""
    field = City._meta.get_field('image')

    assert field.verbose_name == 'Ссылка на изображение'
    assert field.blank is True
    assert field.null is False
    assert field.max_length == 2048
    assert isinstance(field, models.URLField)


def test_city_has_field_image_source_text() -> None:
    """Проверяет поле image_source_text модели City."""
    field = City._meta.get_field('image_source_text')

    assert field.verbose_name == 'Название источника изображения'
    assert field.blank is True
    assert field.null is True
    assert field.max_length == 255
    assert isinstance(field, models.CharField)


def test_city_has_field_image_source_link() -> None:
    """Проверяет поле image_source_link модели City."""
    field = City._meta.get_field('image_source_link')

    assert field.verbose_name == 'Ссылка на источник изображения'
    assert field.blank is True
    assert field.null is True
    assert isinstance(field, models.URLField)


# Тесты методов модели


def test_city_str_method() -> None:
    """Проверяет метод __str__ модели."""
    city = City(title='Test City')
    assert str(city) == 'Test City'


def test_city_get_absolute_url() -> None:
    """Проверяет метод get_absolute_url модели."""
    city = City()
    city.pk = 1
    expected_url = reverse('city-selected', kwargs={'pk': 1})
    assert city.get_absolute_url() == expected_url


# Функциональные тесты


@pytest.fixture
@pytest.mark.django_db
def test_country() -> Country:
    """Фикстура для создания тестовой страны."""
    from country.models import PartOfTheWorld, Location

    part = PartOfTheWorld.objects.create(name='Test')
    location = Location.objects.create(name='Test', part_of_the_world=part)
    return Country.objects.create(
        name='Test Country', code='TC', fullname='Test Country', location=location
    )


@pytest.mark.django_db
def test_city_can_create_without_region(test_country: Country) -> None:
    """Проверяет создание города без региона (регион опционален)."""
    city = City.objects.create(
        title='Test City',
        country=test_country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )

    assert city.title == 'Test City'
    assert city.country == test_country
    assert city.region is None


@pytest.mark.django_db
def test_city_can_create_with_all_fields(test_country: Country) -> None:
    """Проверяет создание города со всеми полями."""
    from region.models import RegionType, Area, Region

    region_type = RegionType.objects.create(title='Область')
    area = Area.objects.create(country=test_country, title='Test Area')
    region = Region.objects.create(
        title='Test Region',
        country=test_country,
        type=region_type,
        area=area,
        iso3166='T-R',
        full_name='Test Region область',
    )

    city = City.objects.create(
        title='Test City',
        country=test_country,
        region=region,
        population=1000000,
        date_of_foundation=1147,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
        wiki='https://ru.wikipedia.org/wiki/Test',
        image='https://example.com/image.jpg',
        image_source_text='Wikipedia',
        image_source_link='https://wikipedia.org',
    )

    assert city.title == 'Test City'
    assert city.country == test_country
    assert city.region == region
    assert city.population == 1000000
    assert city.date_of_foundation == 1147
    assert city.wiki == 'https://ru.wikipedia.org/wiki/Test'
    assert city.image == 'https://example.com/image.jpg'


@pytest.mark.django_db
def test_city_ordering(test_country: Country) -> None:
    """Проверяет сортировку городов по названию."""
    City.objects.create(
        title='Город Б', country=test_country, coordinate_width=55.0, coordinate_longitude=37.0
    )
    City.objects.create(
        title='Город А', country=test_country, coordinate_width=56.0, coordinate_longitude=38.0
    )
    City.objects.create(
        title='Город В', country=test_country, coordinate_width=57.0, coordinate_longitude=39.0
    )

    cities = list(City.objects.values_list('title', flat=True))
    assert cities == ['Город А', 'Город Б', 'Город В']
