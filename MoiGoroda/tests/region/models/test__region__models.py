import pytest
import django

from django.db import transaction

from region.models import Area, Region


@pytest.mark.django_db
def test__region__fields(setup_db):
    """
    Тестирует корректность выставленных настроек модели.
    Для метода __str__() проверяется корректность отображения типа региона.
    """
    assert Region._meta.ordering == ['title']
    assert Region._meta.verbose_name == 'Регион'
    assert Region._meta.verbose_name_plural == 'Регионы'
    assert Region._meta.unique_together == (('title', 'type'),)

    assert Region.objects.get(id=1).__str__() == 'Адыгея'
    assert Region.objects.get(id=2).__str__() == 'Краснодарский край'
    assert Region.objects.get(id=3).__str__() == 'Волгоградская область'
    assert Region.objects.get(id=4).__str__() == 'Севастополь'
    assert Region.objects.get(id=5).__str__() == 'Еврейская автономная область'
    assert Region.objects.get(id=6).__str__() == 'Чукотский автономный округ'
    assert Region.objects.get(id=7).__str__() == 'Чеченская республика'


@pytest.mark.django_db
def test__region__qty_of_lines(setup_db):
    """
    Всего должно создаться 7 записей.
    """
    assert Region.objects.count() == 7


@pytest.mark.django_db
def test__region__unique_iso3166(setup_db):
    """
    Записи с одинаковым полем iso3166 не должны создаваться.
    При попытке это сделать должно выбрасываться исключение django.db.utils.IntegrityError.
    """
    with pytest.raises(django.db.utils.IntegrityError) as exc:
        Region.objects.create(
            area=Area.objects.get(id=1),
            title='Адыгея',
            type='R',
            iso3166='RU-AD'
        )


@pytest.mark.django_db
def test__region__unique_title_and_type(setup_db):
    """
    Записи с одинаковой комбинацией полей title и type не должны создаваться.
    При попытке это сделать должно выбрасываться исключение django.db.utils.IntegrityError.
    """
    with pytest.raises(django.db.utils.IntegrityError) as exc:
        Region.objects.create(
            area=Area.objects.get(id=1),
            title='Адыгея',
            type='R',
            iso3166='RU-AD_UNIQUE'
        )


@pytest.mark.django_db
def test__region__correct_records(setup_db):
    """
    Тестирует корректность заполнения полей таблицы.
    Для республик есть 2 формата отображения - со словом "республик" и без него.
    """
    assert Region.objects.get(id=2).title == 'Краснодарский'
    assert Region.objects.get(id=2).type == 'K'
    assert Region.objects.get(id=2).iso3166 == 'RU-KDA'
