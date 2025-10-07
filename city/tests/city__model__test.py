"""
Тестирует корректность настроек модели City.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from django.db import models

from city.models import City
from region.models import Area, Region


@pytest.fixture
def setup_db(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Area 1')
    region = Region.objects.create(id=1, area=area, title='Регион 1', type='O', iso3166='RU-RU')
    City.objects.create(
        id=1, title='Город 1', region=region, coordinate_width=1, coordinate_longitude=1
    )
    City.objects.create(
        id=2, title='Город 2', region=region, coordinate_width=1, coordinate_longitude=1
    )
    City.objects.create(
        id=3, title='Город 3', region=region, coordinate_width=1, coordinate_longitude=1
    )


@pytest.mark.django_db
def test__verbose_name(setup_db):
    assert City._meta.verbose_name == 'Город'
    assert City._meta.verbose_name_plural == 'Города'


@pytest.mark.django_db
def test__ordering(setup_db):
    queryset = City.objects.values_list('title', flat=True)
    assert City._meta.ordering == ['title']
    assert list(queryset) == ['Город 1', 'Город 2', 'Город 3']


@pytest.mark.django_db
def test__parameters_of_field__title(setup_db):
    assert City._meta.get_field('title').verbose_name == 'Название'
    assert City._meta.get_field('title').blank is False
    assert City._meta.get_field('title').null is False
    assert isinstance(City._meta.get_field('title'), models.CharField)


@pytest.mark.django_db
def test__parameters_of_field__region(setup_db):
    assert City._meta.get_field('region').verbose_name == 'Регион'
    assert City._meta.get_field('region').blank is False
    assert City._meta.get_field('region').null is False
    assert isinstance(City._meta.get_field('region'), models.ForeignKey)


@pytest.mark.django_db
def test__parameters_of_field__population(setup_db):
    assert City._meta.get_field('population').verbose_name == 'Численность населения'
    assert City._meta.get_field('population').blank
    assert City._meta.get_field('population').null
    assert isinstance(City._meta.get_field('population'), models.PositiveIntegerField)


@pytest.mark.django_db
def test__parameters_of_field__date_of_foundation(setup_db):
    assert City._meta.get_field('date_of_foundation').verbose_name == 'Год основания'
    assert City._meta.get_field('date_of_foundation').blank
    assert City._meta.get_field('date_of_foundation').null
    assert isinstance(City._meta.get_field('date_of_foundation'), models.PositiveSmallIntegerField)


@pytest.mark.django_db
def test__parameters_of_field__coordinate_width(setup_db):
    assert City._meta.get_field('coordinate_width').verbose_name == 'Широта'
    assert City._meta.get_field('coordinate_width').blank is False
    assert City._meta.get_field('coordinate_width').null is False
    assert isinstance(City._meta.get_field('coordinate_width'), models.FloatField)


@pytest.mark.django_db
def test__parameters_of_field__coordinate_longitude(setup_db):
    assert City._meta.get_field('coordinate_longitude').verbose_name == 'Долгота'
    assert City._meta.get_field('coordinate_longitude').blank is False
    assert City._meta.get_field('coordinate_longitude').null is False
    assert isinstance(City._meta.get_field('coordinate_longitude'), models.FloatField)


@pytest.mark.django_db
def test__parameters_of_field__wiki(setup_db):
    assert City._meta.get_field('wiki').verbose_name == 'Ссылка на Wikipedia'
    assert City._meta.get_field('wiki').blank
    assert City._meta.get_field('wiki').null
    assert isinstance(City._meta.get_field('wiki'), models.CharField)


@pytest.mark.django_db
def test__str(setup_db):
    assert City.objects.get(id=1).__str__() == 'Город 1'
    assert City.objects.get(id=2).__str__() == 'Город 2'
    assert City.objects.get(id=3).__str__() == 'Город 3'
