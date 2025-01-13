"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import pytest
from django.db import models

from place.models import Category, TagOSM


def test__model_category_can_create_model_instance():
    assert Category()


def test__model_category_has_valid_verbose_name():
    assert Category._meta.verbose_name == 'Категория'
    assert Category._meta.verbose_name_plural == 'Категории'


def test__model_category_has_a_field_name():
    field = Category._meta.get_field('name')

    assert field.verbose_name == 'Название'
    assert field.blank is False
    assert field.null is False
    assert field.unique is False
    assert field.max_length == 255
    assert isinstance(field, models.CharField)


def test__model_category_has_a_field_tags():
    field = Category._meta.get_field('tags')

    assert field.verbose_name == 'Теги OpenStreetMap'
    assert field.blank is True
    assert field.unique is False
    assert isinstance(field, models.ManyToManyField)
    assert isinstance(field.remote_field.model(), TagOSM)


@pytest.mark.django_db
def test__model_typepobject_has_str_representation():
    obj = Category(name='Природа')
    obj.save()

    assert str(obj) == 'Природа'
