"""
Тестирует корректность настроек модели News.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


import pytest

from django.db import models
from mdeditor import fields

from news.models import News


@pytest.fixture
def setup_db__news(django_user_model):
    django_user_model.objects.create_user(username='username', password='password')
    News.objects.create(id=1, title='Заголовок новости 1', content='Content 1')
    News.objects.create(id=2, title='Заголовок новости 2', content='Content 2')
    # News.objects.create(id=1, title='Заголовок новости 1', content='* list1\r\r1. list2')
    # News.objects.create(id=2, title='Заголовок новости 2', content='#H1\r##H2\r###H3\r####H4\r#####H5\r######H6\r'
    #                                                                '**bold1**\r__bold2__\r*italic1*\r_italic2_\r'
    #                                                                '[Link](https://link)\r![Изображение](https://link)\r'
    #                                                                '```somecode1```\r`somecode2`\r> Quoting')


@pytest.mark.django_db
def test__verbose_name(setup_db__news):
    assert News._meta.verbose_name == 'Новость'
    assert News._meta.verbose_name_plural == 'Новости'


@pytest.mark.django_db
def test__ordering(setup_db__news):
    queryset = News.objects.values_list('title', flat=True)

    assert News._meta.ordering == ['-created']
    assert list(queryset) == ['Заголовок новости 2', 'Заголовок новости 1']


@pytest.mark.parametrize(
    'news', (
        (1, 'Заголовок новости 1'),
        (2, 'Заголовок новости 2')
    )
)
@pytest.mark.django_db
def test__str(setup_db__news, news: tuple):
    assert News.objects.get(id=news[0]).__str__() == news[1]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'news', (
        (1, 'Заголовок новости 1', 'Content 1'),
        (2, 'Заголовок новости 2', 'Content 2')
    )
)
def test__filling_of_table(setup_db__news, news: tuple):
    queryset = News.objects.get(id=news[0])

    assert queryset.title == news[1]
    assert queryset.content == news[2]


@pytest.mark.django_db
def test__parameters_of_field__title(setup_db__news):
    assert News._meta.get_field('title').verbose_name == 'Заголовок'
    assert News._meta.get_field('title').blank is False
    assert News._meta.get_field('title').null is False
    assert isinstance(News._meta.get_field('title'), models.CharField)


@pytest.mark.django_db
def test__parameters_of_field__content(setup_db__news):
    assert News._meta.get_field('content').verbose_name == 'Новость'
    assert News._meta.get_field('content').blank is False
    assert News._meta.get_field('content').null is False
    assert isinstance(News._meta.get_field('content'), fields.MDTextField)


@pytest.mark.django_db
def test__parameters_of_field__created(setup_db__news):
    assert News._meta.get_field('created').verbose_name == 'Дата создания'
    assert News._meta.get_field('created').auto_now_add
    assert isinstance(News._meta.get_field('created'), models.DateTimeField)


@pytest.mark.django_db
def test__parameters_of_field__last_modified(setup_db__news):
    assert News._meta.get_field('last_modified').verbose_name == 'Дата изменения'
    assert News._meta.get_field('last_modified').auto_now
    assert isinstance(News._meta.get_field('last_modified'), models.DateTimeField)
