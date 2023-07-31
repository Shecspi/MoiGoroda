"""
Тестирует корректность настроек модели VisitedCity.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


import pytest

from django.db import models

from city.models import City, VisitedCity
from region.models import Area, Region


@pytest.fixture
def setup_db(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Area 1')
    region = Region.objects.create(id=1, area=area, title='Регион 1', type='O', iso3166=f'RU-RU')
    city_1 = City.objects.create(id=1, title='Город 1', region=region, coordinate_width=1, coordinate_longitude=1)
    city_2 = City.objects.create(id=2, title='Город 2', region=region, coordinate_width=1, coordinate_longitude=1)
    city_3 = City.objects.create(id=3, title='Город 3', region=region, coordinate_width=1, coordinate_longitude=1)
    VisitedCity.objects.create(id=1, user=user, region=region, city=city_1, rating=5)
    VisitedCity.objects.create(id=2, user=user, region=region, city=city_2, rating=5)
    VisitedCity.objects.create(id=3, user=user, region=region, city=city_3, rating=5)


@pytest.mark.django_db
def test__verbose_name(setup_db):
    assert VisitedCity._meta.verbose_name == 'Посещённый город'
    assert VisitedCity._meta.verbose_name_plural == 'Посещённые города'


@pytest.mark.django_db
def test__ordering(setup_db):
    queryset = VisitedCity.objects.values_list('city__title', flat=True)
    assert VisitedCity._meta.ordering == ['-id']
    assert list(queryset) == ['Город 3', 'Город 2', 'Город 1']


@pytest.mark.django_db
def test__parameters_of_field__user(setup_db):
    assert VisitedCity._meta.get_field('user').verbose_name == 'Пользователь'
    assert VisitedCity._meta.get_field('user').blank is False
    assert VisitedCity._meta.get_field('user').null is False
    assert isinstance(VisitedCity._meta.get_field('user'), models.ForeignKey)


@pytest.mark.django_db
def test__parameters_of_field__region(setup_db):
    assert VisitedCity._meta.get_field('region').verbose_name == 'Регион'
    assert VisitedCity._meta.get_field('region').blank is False
    assert VisitedCity._meta.get_field('region').null is False
    assert isinstance(VisitedCity._meta.get_field('region'), models.ForeignKey)


@pytest.mark.django_db
def test__parameters_of_field__city(setup_db):
    assert VisitedCity._meta.get_field('city').verbose_name == 'Город'
    assert VisitedCity._meta.get_field('city').blank is False
    assert VisitedCity._meta.get_field('city').null is False
    assert isinstance(VisitedCity._meta.get_field('city'), models.ForeignKey)


@pytest.mark.django_db
def test__parameters_of_field__has_magnet(setup_db):
    assert VisitedCity._meta.get_field('has_magnet').verbose_name == 'Наличие магнита'
    assert VisitedCity._meta.get_field('has_magnet').blank
    assert VisitedCity._meta.get_field('has_magnet').null
    assert isinstance(VisitedCity._meta.get_field('has_magnet'), models.BooleanField)


@pytest.mark.django_db
def test__parameters_of_field__impression(setup_db):
    assert VisitedCity._meta.get_field('impression').verbose_name == 'Впечатления о городе'
    assert VisitedCity._meta.get_field('impression').blank
    assert VisitedCity._meta.get_field('impression').null
    assert isinstance(VisitedCity._meta.get_field('impression'), models.TextField)


@pytest.mark.django_db
def test__parameters_of_field__rating(setup_db):
    assert VisitedCity._meta.get_field('rating').verbose_name == 'Рейтинг'
    assert VisitedCity._meta.get_field('rating').blank is False
    assert VisitedCity._meta.get_field('rating').null is False
    assert isinstance(VisitedCity._meta.get_field('rating'), models.SmallIntegerField)


@pytest.mark.django_db
def test__str(setup_db):
    assert VisitedCity.objects.get(id=1).__str__() == 'Город 1'
    assert VisitedCity.objects.get(id=2).__str__() == 'Город 2'
    assert VisitedCity.objects.get(id=3).__str__() == 'Город 3'
