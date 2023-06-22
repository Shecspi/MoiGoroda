import pytest

from django.db.models import DateTimeField, CharField, TextField

from news.models import News


@pytest.mark.django_db
def test__meta(setup_db):
    """
    Тестирует настройки, прописанные в Meta-классе модели.
    """
    assert News._meta.ordering == ['-created']
    assert News._meta.verbose_name == 'Новость'
    assert News._meta.verbose_name_plural == 'Новости'

    assert News.objects.get(id=1).__str__() == 'Заголовок новости 1'
    assert News.objects.get(id=2).__str__() == 'Заголовок новости 2'


@pytest.mark.django_db
def test__fields(setup_db):
    """
    Тестирует настройки модели и её полей.
    """
    assert News.objects.get(id=1)._meta.get_field('title').verbose_name == 'Заголовок'
    assert News.objects.get(id=1)._meta.get_field('title').blank is False
    assert isinstance(News.objects.get(id=1)._meta.get_field('title'), CharField)

    assert News.objects.get(id=1)._meta.get_field('content').verbose_name == 'Новость'
    assert News.objects.get(id=1)._meta.get_field('content').blank is False
    assert isinstance(News.objects.get(id=1)._meta.get_field('content'), TextField)

    assert News.objects.get(id=1)._meta.get_field('created').verbose_name == 'Создано'
    assert isinstance(News.objects.get(id=1)._meta.get_field('created'), DateTimeField)

    assert News.objects.get(id=1)._meta.get_field('last_modified').verbose_name == 'Изменено'
    assert isinstance(News.objects.get(id=1)._meta.get_field('last_modified'), DateTimeField)


@pytest.mark.django_db
def test__news__qty_of_lines(setup_db):
    """
    Тестирует, что все записи были добавлены в базу данных.
    """
    assert News.objects.all().count() == 2
