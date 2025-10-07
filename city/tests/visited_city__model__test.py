"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

from django import core
from django.contrib.auth.models import User
from django.db import models

from city.models import VisitedCity, City
from region.models import Region


def test__model_visited_city_can_create_model_instance():
    assert VisitedCity()


def test__model_visited_city_has_valid_verbose_name():
    assert VisitedCity._meta.verbose_name == 'Посещённый город'
    assert VisitedCity._meta.verbose_name_plural == 'Посещённые города'


def test__model_visited_city_has_correct_ordering():
    assert VisitedCity._meta.ordering == ['-id']


def test__model_visited_city_has_correct_unique_together():
    correct = ['user', 'city', 'date_of_visit']

    assert ('user', 'city', 'date_of_visit') in VisitedCity._meta.unique_together


def test__model_visited_city_has_a_field_user():
    field = VisitedCity._meta.get_field('user')

    assert field.verbose_name == 'Пользователь'
    assert field.blank is False
    assert field.null is False
    assert field.remote_field.on_delete == models.CASCADE
    assert isinstance(field, models.ForeignKey)
    assert isinstance(field.remote_field.model(), User)


def test__model_visited_city_has_a_field_region():
    field = VisitedCity._meta.get_field('region')

    assert field.verbose_name == 'Регион'
    assert field.blank is False
    assert field.null is False
    assert field.remote_field.on_delete == models.CASCADE
    assert isinstance(field, models.ForeignKey)
    assert isinstance(field.remote_field.model(), Region)


def test__model_visited_city_has_a_field_city():
    field = VisitedCity._meta.get_field('city')

    assert field.verbose_name == 'Город'
    assert field.blank is False
    assert field.null is False
    assert field.remote_field.on_delete == models.CASCADE
    assert isinstance(field, models.ForeignKey)
    assert isinstance(field.remote_field.model(), City)


def test__model_visited_city_has_field_date_of_visit():
    field = VisitedCity._meta.get_field('date_of_visit')

    assert field.verbose_name == 'Дата посещения'
    assert field.blank is True
    assert field.null is True
    assert isinstance(field, models.DateField)


def test__model_visited_city_has_field_has_magnet():
    field = VisitedCity._meta.get_field('has_magnet')

    assert field.verbose_name == 'Наличие сувенира из города'
    assert field.blank is True
    assert field.null is False
    assert isinstance(field, models.BooleanField)
    assert field.default is False


def test__model_visited_city_has_field_impression():
    field = VisitedCity._meta.get_field('impression')

    assert field.verbose_name == 'Впечатления о городе'
    assert field.blank is True
    assert field.null is True
    assert isinstance(field, models.TextField)


def test__model_visited_city_has_field_rating():
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


def test__model_visited_city_has_field_is_first_visit():
    field = VisitedCity._meta.get_field('is_first_visit')

    assert field.verbose_name == 'Первый раз в городе?'
    assert field.blank is True
    assert field.null is True
    assert isinstance(field, models.BooleanField)
    assert field.default is True
