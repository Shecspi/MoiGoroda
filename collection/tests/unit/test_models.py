"""
Юнит-тесты для моделей приложения collection.
"""

from typing import Any

import pytest
from django.db import models

from collection.models import Collection


@pytest.mark.unit
class TestCollectionModel:
    """Тесты для модели Collection."""

    def test_model_has_correct_fields(self) -> None:
        """Проверяет наличие всех необходимых полей модели."""
        assert hasattr(Collection, 'title')
        assert hasattr(Collection, 'city')

    def test_title_field_is_char_field(self) -> None:
        """Проверяет тип поля title."""
        field = Collection._meta.get_field('title')
        assert isinstance(field, models.CharField)

    def test_title_field_max_length(self) -> None:
        """Проверяет максимальную длину поля title."""
        field = Collection._meta.get_field('title')
        assert field.max_length == 256

    def test_title_field_cannot_be_blank(self) -> None:
        """Проверяет что поле title не может быть пустым."""
        field = Collection._meta.get_field('title')
        assert field.blank is False

    def test_city_field_is_many_to_many(self) -> None:
        """Проверяет что поле city является ManyToManyField."""
        field = Collection._meta.get_field('city')
        assert isinstance(field, models.ManyToManyField)

    def test_city_field_related_name(self) -> None:
        """Проверяет related_name поля city."""
        field = Collection._meta.get_field('city')
        assert field.remote_field.related_name == 'collections_list'

    def test_meta_ordering(self) -> None:
        """Проверяет сортировку модели."""
        assert Collection._meta.ordering == ['title']

    def test_meta_verbose_name(self) -> None:
        """Проверяет verbose_name модели."""
        assert Collection._meta.verbose_name == 'Коллекция'

    def test_meta_verbose_name_plural(self) -> None:
        """Проверяет verbose_name_plural модели."""
        assert Collection._meta.verbose_name_plural == 'Коллекции'


@pytest.mark.django_db
@pytest.mark.integration
class TestCollectionModelMethods:
    """Интеграционные тесты для методов модели Collection."""

    @pytest.fixture
    def collection(self) -> Collection:
        """Создает коллекцию для тестов."""
        return Collection.objects.create(title='Тестовая коллекция')

    def test_str_method(self, collection: Collection) -> None:
        """Проверяет метод __str__."""
        assert str(collection) == 'Тестовая коллекция'

    def test_get_absolute_url(self, collection: Collection) -> None:
        """Проверяет метод get_absolute_url."""
        url = collection.get_absolute_url()
        assert url == f'/collection/{collection.pk}/list'
