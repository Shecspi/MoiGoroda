"""
Тестирует корректность настроек модели Area.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from django.db import models

from region.models import Area


@pytest.fixture
def setup_db__model_area(client, django_user_model):
    django_user_model.objects.create_user(username='username', password='password')
    Area.objects.create(id=1, title='Area 1')


@pytest.mark.django_db
def test__verbose_name(setup_db__model_area):
    assert Area._meta.verbose_name == 'Федеральный округ'
    assert Area._meta.verbose_name_plural == 'Федеральные округа'


@pytest.mark.django_db
def test__parameters_of_field__title(setup_db__model_area):
    assert Area._meta.get_field('title').verbose_name == 'Название'
    assert Area._meta.get_field('title').blank is False
    assert Area._meta.get_field('title').null is False
    assert Area._meta.get_field('title').unique is True
    assert isinstance(Area._meta.get_field('title'), models.CharField)


@pytest.mark.django_db
def testt__filling_of_table(setup_db__model_area):
    queryset = Area.objects.get(id=1)
    assert queryset.title == 'Area 1'


@pytest.mark.django_db
def test__str(setup_db__model_area):
    assert Area.objects.get(id=1).__str__() == 'Area 1'
