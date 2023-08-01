import pytest

from django.db import models, transaction

from region.models import Area, Region


@pytest.fixture
def setup_db__model_region():
    areas = [
        (1, 'Южный федеральный округ'),
        (2, 'Дальневосточный федеральный округ'),
        (3, 'Северо-Кавказский федеральный округ')
    ]
    regions = [
        [1, 1, 'Адыгея', 'R', 'RU-AD'],
        [2, 1, 'Краснодарский', 'K', 'RU-KDA'],
        [3, 1, 'Волгоградская', 'O', 'RU-VGG'],
        [4, 1, 'Севастополь', 'G', 'RU-SEV'],
        [5, 2, 'Еврейская', 'AOb', 'RU-YEV'],
        [6, 2, 'Чукотский', 'AOk', 'RU-CHU'],
        [7, 3, 'Чеченская', 'R', 'RU-CE']
    ]
    with transaction.atomic():
        for area in areas:
            area = Area.objects.create(id=area[0], title=area[1])
            for region in regions:
                if region[1] == area.id:
                    Region.objects.create(id=region[0], area=area, title=region[2], type=region[3], iso3166=region[4])


@pytest.mark.django_db
def test__verbose_name(setup_db__model_region):
    assert Region._meta.verbose_name == 'Регион'
    assert Region._meta.verbose_name_plural == 'Регионы'


@pytest.mark.django_db
def test__ordering(setup_db__model_region):
    queryset = Region.objects.values_list('title', flat=True)

    assert Region._meta.ordering == ['title']
    assert list(queryset) == [
        'Адыгея', 'Волгоградская', 'Еврейская', 'Краснодарский', 'Севастополь', 'Чеченская', 'Чукотский'
    ]


@pytest.mark.django_db
def test__unique_fields(setup_db__model_region):
    assert Region._meta.unique_together == (('title', 'type'),)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'region', (
        (1, 'Адыгея', 'R', 'RU-AD'),
        (2, 'Краснодарский', 'K', 'RU-KDA'),
        (3, 'Волгоградская', 'O', 'RU-VGG'),
        (4, 'Севастополь', 'G', 'RU-SEV'),
        (5, 'Еврейская', 'AOb', 'RU-YEV'),
        (6, 'Чукотский', 'AOk', 'RU-CHU'),
        (7, 'Чеченская', 'R', 'RU-CE')
    )
)
def test__filling_of_table(setup_db__model_region, region: tuple):
    queryset = Region.objects.get(id=region[0])

    assert queryset.title == region[1]
    assert queryset.type == region[2]
    assert queryset.iso3166 == region[3]


@pytest.mark.parametrize(
    'region', (
        (1, 'Адыгея'),
        (2, 'Краснодарский край'),
        (3, 'Волгоградская область'),
        (4, 'Севастополь'),
        (5, 'Еврейская автономная область'),
        (6, 'Чукотский автономный округ'),
        (7, 'Чеченская республика')
    )
)
@pytest.mark.django_db
def test__str(setup_db__model_region, region: tuple):
    assert Region.objects.get(id=region[0]).__str__() == region[1]


@pytest.mark.django_db
def test__parameters_of_field__area(setup_db__model_region):
    assert Region._meta.get_field('area').verbose_name == 'Федеральный округ'
    assert Region._meta.get_field('area').blank is False
    assert Region._meta.get_field('area').null is False
    assert isinstance(Region._meta.get_field('area'), models.ForeignKey)


@pytest.mark.django_db
def test__parameters_of_field__title(setup_db__model_region):
    assert Region._meta.get_field('title').verbose_name == 'Название'
    assert Region._meta.get_field('title').blank is False
    assert Region._meta.get_field('title').null is False
    assert isinstance(Region._meta.get_field('title'), models.CharField)


@pytest.mark.django_db
def test__parameters_of_field__type(setup_db__model_region):
    assert Region._meta.get_field('type').verbose_name == 'Тип субъекта'
    assert Region._meta.get_field('type').blank is False
    assert Region._meta.get_field('type').null is False
    assert isinstance(Region._meta.get_field('type'), models.CharField)


@pytest.mark.django_db
def test__parameters_of_field__iso3166(setup_db__model_region):
    assert Region._meta.get_field('iso3166').verbose_name == 'Код ISO3166'
    assert Region._meta.get_field('iso3166').blank is False
    assert Region._meta.get_field('iso3166').null is False
    assert Region._meta.get_field('iso3166').unique is True
    assert isinstance(Region._meta.get_field('iso3166'), models.CharField)
