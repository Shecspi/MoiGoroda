"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

from django.db import models

from place.models import Place, TypeObject


def test__model_place_can_create_model_instance():
    assert Place()


def test__model_place_has_valid_verbose_name():
    assert Place._meta.verbose_name == 'Интересное место'
    assert Place._meta.verbose_name_plural == 'Интересные места'


# def test__model_region_has_correct_ordering():
#     assert Place._meta.ordering == ['title']


def test__model_place_has_a_field_name():
    field = Place._meta.get_field('name')

    assert field.verbose_name == 'Название'
    assert field.blank is False
    assert field.null is False
    assert field.unique is False
    assert field.max_length == 255
    assert isinstance(field, models.CharField)


def test__model_place_has_a_field_latitude():
    field = Place._meta.get_field('latitude')

    assert field.verbose_name == 'Широта'
    assert field.blank is False
    assert field.null is False
    assert field.unique is False
    assert isinstance(field, models.FloatField)


def test__model_place_has_a_field_longitude():
    field = Place._meta.get_field('longitude')

    assert field.verbose_name == 'Долгота'
    assert field.blank is False
    assert field.null is False
    assert field.unique is False
    assert isinstance(field, models.FloatField)


def test__model_place_has_a_field_type_object():
    field = Place._meta.get_field('type_object')

    assert field.verbose_name == 'Тип объекта'
    assert field.blank is False
    assert field.null is False
    assert field.unique is False
    assert field.remote_field.on_delete == models.PROTECT
    assert isinstance(field, models.ForeignKey)
    assert isinstance(field.remote_field.model(), TypeObject)


def test__model_place_has_a_field_created_at():
    field = Place._meta.get_field('created_at')

    assert field.verbose_name == 'Дата и время создания'
    assert field.auto_now_add
    assert isinstance(field, models.DateTimeField)


def test__model_place_has_a_field_updated_at():
    field = Place._meta.get_field('updated_at')

    assert field.verbose_name == 'Дата и время редактирования'
    assert field.auto_now
    assert isinstance(field, models.DateTimeField)


# @pytest.fixture
# def setup_db__model_region():
#     areas = [
#         (1, 'Южный федеральный округ'),
#         (2, 'Дальневосточный федеральный округ'),
#         (3, 'Северо-Кавказский федеральный округ'),
#     ]
#     regions = [
#         [1, 1, 'Адыгея', 'R', 'RU-AD'],
#         [2, 1, 'Краснодарский', 'K', 'RU-KDA'],
#         [3, 1, 'Волгоградская', 'O', 'RU-VGG'],
#         [4, 1, 'Севастополь', 'G', 'RU-SEV'],
#         [5, 2, 'Еврейская', 'AOb', 'RU-YEV'],
#         [6, 2, 'Чукотский', 'AOk', 'RU-CHU'],
#         [7, 3, 'Чеченская', 'R', 'RU-CE'],
#     ]
#     with transaction.atomic():
#         for area in areas:
#             area = Area.objects.create(id=area[0], title=area[1])
#  # """
# Тестирует корректность настроек модели Region.
#
# ----------------------------------------------
#
# Copyright 2023 Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------
# """
#
# import pytest
#
# from django.db import models, transaction
#
# from country.models import Country
# from region.models import Area, Region, TypeOfRegion
#
#            for region in regions:
#                 if region[1] == area.id:
#                     Region.objects.create(
#                         id=region[0], area=area, title=region[2], type=region[3], iso3166=region[4]
#                     )
#
#
#

#
#
# @pytest.mark.django_db
# def test__model_region_has_correct_ordering():
#     assert Region._meta.ordering == ['title']
#
#
# @pytest.mark.django_db
# def test__model_region_has_correct_unique_fields():
#     assert Region._meta.unique_together == (('title', 'type'),)
#
#
# @pytest.mark.parametrize(
#     'region',
#     (
#         (1, 'Адыгея'),
#         (2, 'Краснодарский край'),
#         (3, 'Волгоградская область'),
#         (4, 'Севастополь'),
#         (5, 'Еврейская автономная область'),
#         (6, 'Чукотский автономный округ'),
#         (7, 'Чеченская республика'),
#     ),
# )
# @pytest.mark.django_db
# def test__str(setup_db__model_region, region: tuple):
#     assert Region.objects.get(id=region[0]).__str__() == region[1]
#
#
# @pytest.mark.django_db
# def test__model_region_has_a_field_area():
#     field = Region._meta.get_field('area')
#
#     assert field.verbose_name == 'Федеральный округ'
#     assert field.blank is True
#     assert field.null is True
#     assert field.remote_field.on_delete == models.SET_NULL
#     assert isinstance(field, models.ForeignKey)
#     assert isinstance(field.remote_field.model(), Area)
#
#
# @pytest.mark.django_db
# def test__model_region_has_a_field_country():
#     field = Region._meta.get_field('country')
#
#     assert field.verbose_name == 'Страна'
#     assert field.blank is False
#     assert field.null is False
#     assert field.remote_field.on_delete == models.PROTECT
#     assert isinstance(field, models.ForeignKey)
#     assert isinstance(field.remote_field.model(), Country)
#
#
# @pytest.mark.django_db
# def test__model_region_has_a_field_title():
#     field = Region._meta.get_field('title')
#     assert field.verbose_name == 'Название'
#     assert field.max_length == 100
#     assert field.blank is False
#     assert field.null is False
#     assert isinstance(field, models.CharField)
#
#
# @pytest.mark.django_db
# def test__model_region_has_a_field_type_of_region():
#     field = Region._meta.get_field('type')
#
#     assert field.verbose_name == 'Тип субъекта'
#     assert field.blank is False
#     assert field.null is False
#     assert field.remote_field.on_delete == models.PROTECT
#     assert isinstance(field, models.ForeignKey)
#     assert isinstance(field.remote_field.model(), TypeOfRegion)
#
#
# @pytest.mark.django_db
# def test__model_region_has_a_field_code():
#     field = Region._meta.get_field('iso3166')
#
#     assert field.verbose_name == 'Код ISO 3166-2'
#     assert field.max_length == 10
#     assert field.unique is True
#     assert field.blank is False
#     assert field.null is False
#     assert isinstance(field, models.CharField)
