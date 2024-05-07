"""

Copyright 2024 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import pytest

from django.db import models
from mdeditor import fields

from news.models import News


@pytest.mark.django_db
def test__verbose_name(setup):
    assert News._meta.verbose_name == 'Новость'
    assert News._meta.verbose_name_plural == 'Новости'


@pytest.mark.django_db
def test__ordering(setup):
    queryset = News.objects.values_list('title', flat=True)

    assert News._meta.ordering == ['-created']
    assert list(queryset) == [
        'Заголовок новости 4',
        'Заголовок новости 3',
        'Заголовок новости 2',
        'Заголовок новости 1',
    ]


@pytest.mark.parametrize(
    'news',
    (
        (1, 'Заголовок новости 1'),
        (2, 'Заголовок новости 2'),
        (3, 'Заголовок новости 3'),
        (4, 'Заголовок новости 4'),
    ),
)
@pytest.mark.django_db
def test__str(setup, news: tuple):
    assert News.objects.get(id=news[0]).__str__() == news[1]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'news', ((1, 'Заголовок новости 1', 'Content 1'), (2, 'Заголовок новости 2', 'Content 2'))
)
def test__filling_of_table(setup, news: tuple):
    queryset = News.objects.get(id=news[0])

    assert queryset.title == news[1]
    assert queryset.content == news[2]


@pytest.mark.django_db
def test__parameters_of_field__title(setup):
    assert News._meta.get_field('title').verbose_name == 'Заголовок'
    assert News._meta.get_field('title').blank is False
    assert News._meta.get_field('title').null is False
    assert isinstance(News._meta.get_field('title'), models.CharField)


@pytest.mark.django_db
def test__parameters_of_field__content(setup):
    assert News._meta.get_field('content').verbose_name == 'Новость'
    assert News._meta.get_field('content').blank is False
    assert News._meta.get_field('content').null is False
    assert isinstance(News._meta.get_field('content'), fields.MDTextField)


@pytest.mark.django_db
def test__parameters_of_field__created(setup):
    assert News._meta.get_field('created').verbose_name == 'Дата создания'
    assert News._meta.get_field('created').auto_now_add
    assert isinstance(News._meta.get_field('created'), models.DateTimeField)


@pytest.mark.django_db
def test__parameters_of_field__last_modified(setup):
    assert News._meta.get_field('last_modified').verbose_name == 'Дата изменения'
    assert News._meta.get_field('last_modified').auto_now
    assert isinstance(News._meta.get_field('last_modified'), models.DateTimeField)
