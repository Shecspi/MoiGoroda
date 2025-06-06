import pytest
from django.core.exceptions import ValidationError
from country.models import Country
from region.models import Area


@pytest.fixture
def fake_country():
    return Country(name='Фейковая страна', code='FC')


@pytest.fixture
def area_instance(fake_country):
    return Area(title='Приволжский', country=fake_country)


def test_area_model_structure():
    expected_fields = {'id', 'title', 'country'}
    model_fields = {f.name for f in Area._meta.get_fields() if not f.auto_created or f.name == 'id'}
    assert (
        model_fields == expected_fields
    ), 'Модель Area изменилась. Обновите тесты и добавьте проверки для новых полей.'


def test_area_str(area_instance):
    assert str(area_instance) == 'Приволжский'


def test_area_field_title_options():
    field = Area._meta.get_field('title')
    assert not field.null
    assert not field.blank
    assert field.unique
    assert field.verbose_name == 'Название'
    assert field.max_length == 100


def test_area_field_country_options():
    field = Area._meta.get_field('country')
    assert not field.null
    assert not field.blank
    assert not field.unique
    assert field.verbose_name == 'Страна'


def test_area_meta_options():
    assert Area._meta.verbose_name == 'Федеральный округ'
    assert Area._meta.verbose_name_plural == 'Федеральные округа'


def test_area_field_required():
    area = Area(title=None, country=None)
    with pytest.raises(ValidationError) as exc_info:
        area.full_clean()

    errors = exc_info.value.message_dict
    assert 'title' in errors
    assert 'country' in errors
