"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import pytest
from django.db import models

from place.models import TagOSM


def test__model_tagosm_can_create_model_instance():
    assert TagOSM()


def test__model_tagosm_has_valid_verbose_name():
    assert TagOSM._meta.verbose_name == 'Тег'
    assert TagOSM._meta.verbose_name_plural == 'Теги'


def test__model_tagosm_has_a_field_name():
    field = TagOSM._meta.get_field('name')

    assert field.verbose_name == 'Название'
    assert field.blank is False
    assert field.null is False
    assert field.unique is False
    assert field.max_length == 255
    assert isinstance(field, models.CharField)


@pytest.mark.django_db
def test__model_tagosm_has_str_representation():
    obj = TagOSM.objects.create(name='water')

    assert str(obj) == 'water'
