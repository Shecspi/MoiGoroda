"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

from itertools import zip_longest

from django.contrib import admin

from place.models import TagOSM


def test__model_tagosm_is_registered_in_admin():
    assert admin.site.is_registered(TagOSM)


def test__model_tagosm_has_correct_list_display_in_admin():
    correct = ('name',)
    list_display = admin.site._registry[TagOSM].list_display

    # list_display может быть как кортежем, так и списком, поэтому нужно сравнивать поэлементно
    assert all([i == j for i, j in zip_longest(correct, list_display)])


def test__model_tagosm_has_correct_list_filter_in_admin():
    correct = ('name',)
    list_filter = admin.site._registry[TagOSM].list_filter

    # list_display может быть как кортежем, так и списком, поэтому нужно сравнивать поэлементно
    assert all([i == j for i, j in zip_longest(correct, list_filter)])


def test__model_tagosm_has_correct_search_fields_in_admin():
    correct = ('name',)
    search_fields = admin.site._registry[TagOSM].search_fields

    # list_display может быть как кортежем, так и списком, поэтому нужно сравнивать поэлементно
    assert all([i == j for i, j in zip_longest(correct, search_fields)])
