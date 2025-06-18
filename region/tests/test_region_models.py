import pytest
from django.core.exceptions import ValidationError

from region.models import Region, Area
from country.models import Country


@pytest.fixture
def fake_country():
    return Country(name='Фейковая страна', code='FC')


@pytest.fixture
def fake_area():
    return Area(title='Фейковый макрорегион')


@pytest.fixture
def region_instance(fake_country, fake_area):
    return Region(
        title='Фейковый регион', type='O', iso3166='FAKE-REG', country=fake_country, area=fake_area
    )


def test_region_model_structure():
    expected_fields = {
        'title',
        'type',
        'iso3166',
        'country',
        'area',
    }
    model_fields = set(f.name for f in Region._meta.get_fields() if not f.auto_created)
    assert (
        model_fields == expected_fields
    ), 'Модель Region изменилась. Обновите тесты и добавьте тесты для новых полей.'


def test_region_str(region_instance):
    assert str(region_instance) == 'Фейковый регион область'


def test_region_fields_required():
    region = Region(title=None, type=None, iso3166=None, country=None)
    with pytest.raises(ValidationError) as exc_info:
        region.full_clean()

    errors = exc_info.value.message_dict
    assert 'title' in errors
    assert 'type' in errors
    assert 'iso3166' in errors
    assert 'country' in errors


def test_region_meta_options():
    assert Region._meta.verbose_name == 'Регион'
    assert Region._meta.verbose_name_plural == 'Регионы'
    assert Region._meta.ordering == ['title']


def test_region_field_values(region_instance):
    assert region_instance.title == 'Фейковый регион'
    assert region_instance.type == 'O'
    assert region_instance.iso3166 == 'FAKE-REG'
    assert region_instance.country.__str__() == 'Фейковая страна'
    assert region_instance.area.__str__() == 'Фейковый макрорегион'


@pytest.mark.parametrize(
    'title,expected',
    [
        ('Кабардино-Балкарская', 'Кабардино-Балкарская республика'),
        ('Карачаево-Черкесская', 'Карачаево-Черкесская республика'),
        ('Удмуртская', 'Удмуртская республика'),
        ('Чеченская', 'Чеченская республика'),
        ('Чувашская', 'Чувашская республика'),
        ('Татарстан', 'Татарстан'),  # не входит в особые
    ],
)
def test_region_str_republics(title, expected, fake_country, fake_area):
    region = Region(title=title, type='R', iso3166='ISO-R1', country=fake_country, area=fake_area)
    assert str(region) == expected


@pytest.mark.parametrize(
    'title,type_code,type_display,expected',
    [
        ('Пермский', 'K', 'Край', 'Пермский край'),
        ('Самарская', 'O', 'Область', 'Самарская область'),
        ('Еврейская', 'A', 'Автономная область', 'Еврейская автономная область'),
    ],
)
def test_region_str_other_types(
    monkeypatch, title, type_code, type_display, expected, fake_country, fake_area
):
    region = Region(
        title=title, type=type_code, iso3166='ISO-X', country=fake_country, area=fake_area
    )

    # monkeypatch get_type_display
    monkeypatch.setattr(region, 'get_type_display', lambda: type_display)
    assert str(region) == expected
