"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

from django.db import models

from place.models import TypeObject, TagOSM


def test__model_typeobject_can_create_model_instance():
    assert TypeObject()


def test__model_typeobject_has_valid_verbose_name():
    assert TypeObject._meta.verbose_name == 'Тип объекта'
    assert TypeObject._meta.verbose_name_plural == 'Типы объектов'


def test__model_typeobject_has_a_field_name():
    field = TypeObject._meta.get_field('name')

    assert field.verbose_name == 'Название'
    assert field.blank is False
    assert field.null is False
    assert field.unique is False
    assert field.max_length == 255
    assert isinstance(field, models.CharField)


def test__model_typeobject_has_a_field_tags():
    field = TypeObject._meta.get_field('tags')

    assert field.verbose_name == 'Теги OpenStreetMap'
    assert field.blank is True
    assert field.null is True
    assert field.unique is False
    assert isinstance(field, models.ManyToManyField)
    assert isinstance(field.remote_field.model(), TagOSM)
