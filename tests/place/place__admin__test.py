"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

from itertools import zip_longest

from django.contrib import admin

from place.models import Place


def test__model_place_is_registered_in_admin():
    assert admin.site.is_registered(Place)


def test__model_place_has_correct_list_display_in_admin():
    correct = ('name', 'latitude', 'longitude', 'type_object', 'created_at', 'updated_at')
    list_display = admin.site._registry[Place].list_display

    # list_display может быть как кортежем, так и списком, поэтому нужно сравнивать поэлементно
    assert all([i == j for i, j in zip_longest(correct, list_display)])


def test__model_place_has_correct_list_filter_in_admin():
    # На данный момент для этой модели не предусмотрено фильтров
    correct = tuple()
    list_filter = admin.site._registry[Place].list_filter

    # list_display может быть как кортежем, так и списком, поэтому нужно сравнивать поэлементно
    assert all([i == j for i, j in zip_longest(correct, list_filter)])


def test__model_place_has_correct_search_field_in_admin():
    correct = ('name',)
    search_fields = admin.site._registry[Place].search_fields

    # list_display может быть как кортежем, так и списком, поэтому нужно сравнивать поэлементно
    assert all([i == j for i, j in zip_longest(correct, search_fields)])
