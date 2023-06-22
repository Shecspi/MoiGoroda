import django
import pytest
from django.db import transaction

from region.models import Area


@pytest.mark.django_db
def test__area__fields(setup_db):
    """
    Тестирует корректность выставленных настроек модели.
    """
    assert Area._meta.verbose_name == 'Федеральный округ'
    assert Area._meta.verbose_name_plural == 'Федеральные округа'


@pytest.mark.django_db
def test__area__qty_of_lines(setup_db):
    """
    Всего должно создаться 3 записи.
    """
    assert Area.objects.count() == 3


@pytest.mark.django_db
def test__area__unique_title(setup_db):
    """
    Записи с одинаковым полем title не должны создаваться.
    При попытке это сделать должно выбрасываться исключение django.db.utils.IntegrityError.
    """
    with pytest.raises(django.db.utils.IntegrityError) as exc:
        Area.objects.create(title='Южный федеральный округ')


@pytest.mark.django_db
def test__area__correct_records(setup_db):
    """
    Тестирует корректность заполнения полей таблицы.
    """
    assert Area.objects.get(id=1).title == 'Южный федеральный округ'
    assert Area.objects.get(id=2).title == 'Дальневосточный федеральный округ'
    assert Area.objects.get(id=1).__str__() == 'Южный федеральный округ'
    assert Area.objects.get(id=2).__str__() == 'Дальневосточный федеральный округ'
