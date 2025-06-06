import pytest
from django.core.exceptions import ValidationError

from city.models import City
from country.models import Country
from region.models import Region


@pytest.fixture
def fake_country():
    return Country(name='Фейковая страна', code='FC')


@pytest.fixture
def fake_region():
    return Region(title='Фейковый регион', type='O', iso3166='FAKE-REG', country=None, area=None)


@pytest.fixture
def city_instance(fake_country, fake_region):
    return City(
        title='Test City',
        country=fake_country,
        region=fake_region,
        population=500_000,
        date_of_foundation=1800,
        coordinate_width=55.75,
        coordinate_longitude=37.61,
        wiki='https://en.wikipedia.org/wiki/Test_City',
        image='https://example.com/test_city.jpg',
        image_source_text='Example Source',
        image_source_link='https://example.com/source',
    )


def test_city_model_structure():
    expected_fields = {
        'title',
        'country',
        'region',
        'population',
        'date_of_foundation',
        'coordinate_width',
        'coordinate_longitude',
        'wiki',
        'image',
        'image_source_text',
        'image_source_link',
    }
    model_fields = set(f.name for f in City._meta.get_fields() if not f.auto_created)
    assert (
        model_fields == expected_fields
    ), 'Модель City изменилась. Обновите тесты и добавьте тесты для новых полей.'


def test_city_str(city_instance):
    assert str(city_instance) == 'Test City'


def test_city_get_absolute_url(city_instance):
    city_instance.pk = 123
    assert city_instance.get_absolute_url() == '/city/123'


def test_city_fields_required(fake_country, fake_region):
    city = City(
        title=None, country=None, region=None, coordinate_width=None, coordinate_longitude=None
    )
    with pytest.raises(ValidationError) as exc_info:
        city.full_clean()

    errors = exc_info.value.message_dict

    assert 'title' in errors
    assert 'country' in errors
    assert 'region' in errors
    assert 'coordinate_width' in errors
    assert 'coordinate_longitude' in errors


def test_city_meta_options():
    assert City._meta.verbose_name == 'Город'
    assert City._meta.verbose_name_plural == 'Города'
    assert City._meta.ordering == ['title']


def test_city_field_values(city_instance):
    assert city_instance.title == 'Test City'
    assert city_instance.country.__str__() == 'Фейковая страна'
    assert city_instance.region.__str__() == 'Фейковый регион область'
    assert city_instance.population == 500_000
    assert city_instance.date_of_foundation == 1800
    assert city_instance.coordinate_width == 55.75
    assert city_instance.coordinate_longitude == 37.61
    assert city_instance.wiki == 'https://en.wikipedia.org/wiki/Test_City'
    assert city_instance.image == 'https://example.com/test_city.jpg'
    assert city_instance.image_source_text == 'Example Source'
    assert city_instance.image_source_link == 'https://example.com/source'
