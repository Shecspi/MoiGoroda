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
@pytest.mark.parametrize(
    'area_name', [
        'Южный федеральный округ',
        'Дальневосточный федеральный округ',
        'Северо-Кавказский федеральный округ',
    ]
)
def test__area__unique_title(setup_db, area_name):
    """
    Записи с одинаковым полем title не должны создаваться.
    При попытке это сделать должно выбрасываться исключение django.db.utils.IntegrityError.
    """
    with pytest.raises(django.db.utils.IntegrityError) as exc:
        Area.objects.create(title=area_name)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'area_id, expected_value', [
        (1, ('Южный федеральный округ', 'Южный федеральный округ')),
        (2, ('Дальневосточный федеральный округ', 'Дальневосточный федеральный округ')),
        (3, ('Северо-Кавказский федеральный округ', 'Северо-Кавказский федеральный округ')),
    ]
)
def test__area__correct_records(setup_db, area_id, expected_value):
    """
    Тестирует корректность заполнения полей таблицы.
    """
    assert Area.objects.get(id=area_id).title == expected_value[0]
    assert Area.objects.get(id=area_id).__str__() == expected_value[1]
