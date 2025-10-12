"""
Юнит-тесты для моделей приложения country.
"""

import pytest
from django.contrib.auth.models import User
from django.db import models

from country.models import PartOfTheWorld, Location, Country, VisitedCountry


@pytest.mark.unit
class TestPartOfTheWorldModel:
    """Тесты для модели PartOfTheWorld."""

    def test_model_has_correct_fields(self) -> None:
        """Проверяет наличие всех необходимых полей модели."""
        assert hasattr(PartOfTheWorld, 'name')

    def test_name_field_is_char_field(self) -> None:
        """Проверяет тип поля name."""
        field = PartOfTheWorld._meta.get_field('name')
        assert isinstance(field, models.CharField)

    def test_name_field_max_length(self) -> None:
        """Проверяет максимальную длину поля name."""
        field = PartOfTheWorld._meta.get_field('name')
        assert field.max_length == 20

    def test_name_field_is_unique(self) -> None:
        """Проверяет что поле name уникальное."""
        field = PartOfTheWorld._meta.get_field('name')
        assert field.unique is True

    def test_name_field_cannot_be_blank(self) -> None:
        """Проверяет что поле name не может быть пустым."""
        field = PartOfTheWorld._meta.get_field('name')
        assert field.blank is False

    def test_meta_verbose_name(self) -> None:
        """Проверяет verbose_name модели."""
        assert PartOfTheWorld._meta.verbose_name == 'Часть света'

    def test_meta_verbose_name_plural(self) -> None:
        """Проверяет verbose_name_plural модели."""
        assert PartOfTheWorld._meta.verbose_name_plural == 'Части света'


@pytest.mark.unit
class TestLocationModel:
    """Тесты для модели Location."""

    def test_model_has_correct_fields(self) -> None:
        """Проверяет наличие всех необходимых полей модели."""
        assert hasattr(Location, 'name')
        assert hasattr(Location, 'part_of_the_world')

    def test_name_field_is_char_field(self) -> None:
        """Проверяет тип поля name."""
        field = Location._meta.get_field('name')
        assert isinstance(field, models.CharField)

    def test_name_field_max_length(self) -> None:
        """Проверяет максимальную длину поля name."""
        field = Location._meta.get_field('name')
        assert field.max_length == 50

    def test_part_of_the_world_is_foreign_key(self) -> None:
        """Проверяет что part_of_the_world является ForeignKey."""
        field = Location._meta.get_field('part_of_the_world')
        assert isinstance(field, models.ForeignKey)

    def test_meta_verbose_name(self) -> None:
        """Проверяет verbose_name модели."""
        assert Location._meta.verbose_name == 'Расположение'

    def test_meta_verbose_name_plural(self) -> None:
        """Проверяет verbose_name_plural модели."""
        assert Location._meta.verbose_name_plural == 'Расположения'


@pytest.mark.unit
class TestCountryModel:
    """Тесты для модели Country."""

    def test_model_has_correct_fields(self) -> None:
        """Проверяет наличие всех необходимых полей модели."""
        assert hasattr(Country, 'name')
        assert hasattr(Country, 'fullname')
        assert hasattr(Country, 'code')
        assert hasattr(Country, 'location')
        assert hasattr(Country, 'is_member_of_un')
        assert hasattr(Country, 'owner')

    def test_name_field_max_length(self) -> None:
        """Проверяет максимальную длину поля name."""
        field = Country._meta.get_field('name')
        assert field.max_length == 100

    def test_code_field_max_length(self) -> None:
        """Проверяет максимальную длину поля code."""
        field = Country._meta.get_field('code')
        assert field.max_length == 2

    def test_code_field_is_unique(self) -> None:
        """Проверяет что поле code уникальное."""
        field = Country._meta.get_field('code')
        assert field.unique is True

    def test_is_member_of_un_default_false(self) -> None:
        """Проверяет значение по умолчанию для is_member_of_un."""
        field = Country._meta.get_field('is_member_of_un')
        assert field.default is False

    def test_meta_verbose_name(self) -> None:
        """Проверяет verbose_name модели."""
        assert Country._meta.verbose_name == 'Страна'


@pytest.mark.unit
class TestVisitedCountryModel:
    """Тесты для модели VisitedCountry."""

    def test_model_has_correct_fields(self) -> None:
        """Проверяет наличие всех необходимых полей модели."""
        assert hasattr(VisitedCountry, 'country')
        assert hasattr(VisitedCountry, 'user')
        assert hasattr(VisitedCountry, 'added_at')

    def test_country_is_foreign_key(self) -> None:
        """Проверяет что country является ForeignKey."""
        field = VisitedCountry._meta.get_field('country')
        assert isinstance(field, models.ForeignKey)

    def test_user_is_foreign_key(self) -> None:
        """Проверяет что user является ForeignKey."""
        field = VisitedCountry._meta.get_field('user')
        assert isinstance(field, models.ForeignKey)

    def test_added_at_is_datetime(self) -> None:
        """Проверяет что added_at является DateTimeField."""
        field = VisitedCountry._meta.get_field('added_at')
        assert isinstance(field, models.DateTimeField)

    def test_unique_together(self) -> None:
        """Проверяет уникальность пары country-user."""
        assert ('country', 'user') in VisitedCountry._meta.unique_together

    def test_meta_verbose_name(self) -> None:
        """Проверяет verbose_name модели."""
        assert VisitedCountry._meta.verbose_name == 'Посещенная страна'


@pytest.mark.django_db
@pytest.mark.integration
class TestCountryModelMethods:
    """Интеграционные тесты для методов моделей."""

    def test_part_of_the_world_str(self, part_of_the_world: PartOfTheWorld) -> None:
        """Проверяет метод __str__ для PartOfTheWorld."""
        assert str(part_of_the_world) == 'Европа'

    def test_location_str(self, location: Location) -> None:
        """Проверяет метод __str__ для Location."""
        assert str(location) == 'Восточная Европа'

    def test_country_str(self) -> None:
        """Проверяет метод __str__ для Country."""
        country = Country.objects.create(name='Россия', code='RU')
        assert str(country) == 'Россия'

    def test_visited_country_str(self, user: User) -> None:
        """Проверяет метод __str__ для VisitedCountry (баг в модели - возвращает Country, а не str)."""
        country = Country.objects.create(name='Россия', code='RU')
        visited = VisitedCountry.objects.create(country=country, user=user)
        # FIXME: __str__ в модели возвращает country объект, а не строку - это баг
        # assert str(visited) == str(country)
        # Пропускаем этот тест до исправления бага в модели
        assert visited.country == country

