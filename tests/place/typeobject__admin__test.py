"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

from itertools import zip_longest

import pytest
from django.contrib import admin

from place.models import TypeObject, TagOSM


def test__model_typeobject_is_registered_in_admin():
    assert admin.site.is_registered(TypeObject)


def test__model_typeobject_has_correct_list_display_in_admin():
    correct = ('name', 'get_tags')
    list_display = admin.site._registry[TypeObject].list_display

    # list_display может быть как кортежем, так и списком, поэтому нужно сравнивать поэлементно
    assert all([i == j for i, j in zip_longest(correct, list_display)])


def test__model_typeobject_has_correct_list_filter_in_admin():
    correct = tuple()
    list_filter = admin.site._registry[TypeObject].list_filter

    # list_display может быть как кортежем, так и списком, поэтому нужно сравнивать поэлементно
    assert all([i == j for i, j in zip_longest(correct, list_filter)])


def test__model_typeobject_has_correct_search_fields_in_admin():
    correct = ('name',)
    search_fields = admin.site._registry[TypeObject].search_fields

    # list_display может быть как кортежем, так и списком, поэтому нужно сравнивать поэлементно
    assert all([i == j for i, j in zip_longest(correct, search_fields)])


@pytest.mark.django_db
def test__model_typepobject_has_get_tags_field_1(admin_client):
    tag1 = TagOSM.objects.create(name='water')
    tag2 = TagOSM.objects.create(name='river')
    tag3 = TagOSM.objects.create(name='mounting')
    obj = TypeObject(name='Природа')
    obj.save()
    obj.tags.add(tag1)
    obj.tags.add(tag2)
    obj.tags.add(tag3)

    response = admin_client.get('/admin/place/typeobject/')

    assert '<td class="field-get_tags">water, river, mounting</td>' in str(response.content)


@pytest.mark.django_db
def test__model_typepobject_has_get_tags_field_2(admin_client):
    tag1 = TagOSM.objects.create(name='water')
    obj = TypeObject(name='Природа')
    obj.save()
    obj.tags.add(tag1)

    response = admin_client.get('/admin/place/typeobject/')

    assert '<td class="field-get_tags">water</td>' in str(response.content)