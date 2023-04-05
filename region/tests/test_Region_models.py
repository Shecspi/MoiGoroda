import django
import pytest
from django.db import transaction

from region.models import Area, Region


@pytest.fixture
def setup_db():
    areas = ['Южный федеральный округ', 'Дальневосточный федеральный округ']
    regions = [
        [1, 'Адыгея', 'R', 'RU-AD'],
        [1, 'Краснодарский', 'K', 'RU-KDA'],
        [1, 'Волгоградская', 'O', 'RU-VGG'],
        [1, 'Севастополь', 'G', 'RU-SEV'],
        [2, 'Еврейская автоновная', 'AOb', 'RU-YEV'],
        [2, 'Чукотский автономный', 'AOk', 'RU-CHU']
    ]
    with transaction.atomic():
        for area in areas:
            area = Area.objects.create(
                title=area
            )
            for region in regions:
                if region[0] == area.id:
                    region = Region.objects.create(
                        area=area,
                        title=region[1],
                        type=region[2],
                        iso3166=region[3]
                    )


@pytest.mark.django_db
def test__area__qty_of_lines(setup_db):
    """
    Всего должно создаться 2 записи.
    """
    assert Area.objects.count() == 2


@pytest.mark.django_db
def test__area__unique_title(setup_db):
    """
    Записи с одинаковым полем title не должны создаваться.
    При попытке это сделать должно выбрасываться исключение django.db.utils.IntegrityError.
    """
    with pytest.raises(django.db.utils.IntegrityError) as exc:
        Area.objects.create(title='Южный федеральный округ')


@pytest.mark.django_db
def test__area__check_correct_fields(setup_db):
    assert Area.objects.get(id=1).title == 'Южный федеральный округ'
    assert Area.objects.get(id=2).title == 'Дальневосточный федеральный округ'


@pytest.mark.django_db
def test__region__qty_of_lines(setup_db):
    """
    Всего должно создаться 6 записей.
    """
    assert Region.objects.count() == 6


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
