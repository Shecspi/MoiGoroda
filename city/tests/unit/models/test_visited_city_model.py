"""
Unit тесты для модели VisitedCity (city/models.py).

Проверяется:
- Структура модели (поля, типы, параметры)
- Meta настройки (ordering, unique_together)
- Валидаторы полей
- Методы модели
"""

import pytest
from django.core.validators import MaxValueValidator, MinValueValidator

from city.models import VisitedCity


@pytest.mark.unit
class TestVisitedCityModelStructure:
    """Тесты структуры модели VisitedCity."""

    def test_model_has_user_field(self) -> None:
        """Модель имеет поле user."""
        field = VisitedCity._meta.get_field('user')

        assert field is not None
        assert field.get_internal_type() == 'ForeignKey'
        assert field.null is False
        assert field.blank is False

    def test_model_has_city_field(self) -> None:
        """Модель имеет поле city."""
        field = VisitedCity._meta.get_field('city')

        assert field is not None
        assert field.get_internal_type() == 'ForeignKey'
        assert field.null is False
        assert field.blank is False

    def test_model_has_date_of_visit_field(self) -> None:
        """Модель имеет поле date_of_visit."""
        field = VisitedCity._meta.get_field('date_of_visit')

        assert field is not None
        assert field.get_internal_type() == 'DateField'
        assert field.null is True
        assert field.blank is True
        assert field.db_index is True  # type: ignore[attr-defined]

    def test_model_has_has_magnet_field(self) -> None:
        """Модель имеет поле has_magnet."""
        field = VisitedCity._meta.get_field('has_magnet')

        assert field is not None
        assert field.get_internal_type() == 'BooleanField'
        assert field.null is False
        assert field.default is False

    def test_model_has_impression_field(self) -> None:
        """Модель имеет поле impression."""
        field = VisitedCity._meta.get_field('impression')

        assert field is not None
        assert field.get_internal_type() == 'TextField'
        assert field.null is True
        assert field.blank is True

    def test_model_has_rating_field(self) -> None:
        """Модель имеет поле rating."""
        field = VisitedCity._meta.get_field('rating')

        assert field is not None
        assert field.get_internal_type() == 'SmallIntegerField'
        assert field.null is False
        assert field.blank is False
        assert field.db_index is True  # type: ignore[attr-defined]

    def test_model_has_is_first_visit_field(self) -> None:
        """Модель имеет поле is_first_visit."""
        field = VisitedCity._meta.get_field('is_first_visit')

        assert field is not None
        assert field.get_internal_type() == 'BooleanField'
        assert field.null is True
        assert field.default is True
        assert field.db_index is True  # type: ignore[attr-defined]


@pytest.mark.unit
class TestVisitedCityModelValidators:
    """Тесты валидаторов модели."""

    def test_rating_has_min_validator(self) -> None:
        """Поле rating имеет MinValueValidator."""
        field = VisitedCity._meta.get_field('rating')
        validators = field.validators

        min_validators = [v for v in validators if isinstance(v, MinValueValidator)]
        assert len(min_validators) == 1
        assert min_validators[0].limit_value == 1

    def test_rating_has_max_validator(self) -> None:
        """Поле rating имеет MaxValueValidator."""
        field = VisitedCity._meta.get_field('rating')
        validators = field.validators

        max_validators = [v for v in validators if isinstance(v, MaxValueValidator)]
        assert len(max_validators) == 1
        assert max_validators[0].limit_value == 5

    def test_rating_has_exactly_two_validators(self) -> None:
        """Поле rating имеет ровно 2 валидатора."""
        field = VisitedCity._meta.get_field('rating')
        validators = field.validators

        assert len(validators) == 2


@pytest.mark.unit
class TestVisitedCityModelMeta:
    """Тесты Meta настроек модели."""

    def test_model_ordering(self) -> None:
        """Проверка порядка сортировки по умолчанию."""
        ordering = VisitedCity._meta.ordering

        assert ordering == ['-id']

    def test_model_verbose_name(self) -> None:
        """Проверка verbose_name."""
        verbose_name = VisitedCity._meta.verbose_name

        assert verbose_name == 'Посещённый город'

    def test_model_verbose_name_plural(self) -> None:
        """Проверка verbose_name_plural."""
        verbose_name_plural = VisitedCity._meta.verbose_name_plural

        assert verbose_name_plural == 'Посещённые города'

    def test_model_unique_together(self) -> None:
        """Проверка unique_together."""
        _unique_together = VisitedCity._meta.unique_together


@pytest.mark.unit
class TestVisitedCityModelMethods:
    """Тесты методов модели."""

    def test_get_absolute_url_returns_correct_path(self) -> None:
        """Метод get_absolute_url возвращает правильный URL."""
        visited_city = VisitedCity(pk=42)

        url = visited_city.get_absolute_url()

        assert url == '/city/42'

    def test_get_absolute_url_with_different_ids(self) -> None:
        """Метод get_absolute_url работает с разными ID."""
        for pk in [1, 100, 9999]:
            visited_city = VisitedCity(pk=pk)
            url = visited_city.get_absolute_url()
            assert url == f'/city/{pk}'
