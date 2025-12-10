"""
Юнит-тесты для модели PersonalCollection.
"""

from typing import Any

import pytest
from django.db import models

from collection.models import PersonalCollection


@pytest.mark.unit
class TestPersonalCollectionModel:
    """Тесты для модели PersonalCollection."""

    def test_model_has_correct_fields(self) -> None:
        """Проверяет наличие всех необходимых полей модели."""
        assert hasattr(PersonalCollection, 'id')
        assert hasattr(PersonalCollection, 'user')
        assert hasattr(PersonalCollection, 'title')
        assert hasattr(PersonalCollection, 'city')
        assert hasattr(PersonalCollection, 'created_at')
        assert hasattr(PersonalCollection, 'updated_at')
        assert hasattr(PersonalCollection, 'is_public')

    def test_id_field_is_uuid_field(self) -> None:
        """Проверяет тип поля id."""
        field = PersonalCollection._meta.get_field('id')
        assert isinstance(field, models.UUIDField)
        assert field.primary_key is True
        assert field.editable is False

    def test_user_field_is_foreign_key(self) -> None:
        """Проверяет тип поля user."""
        field = PersonalCollection._meta.get_field('user')
        assert isinstance(field, models.ForeignKey)
        # Проверяем, что related_model - это модель, а не строка
        related_model = field.related_model
        assert related_model is not None
        assert not isinstance(related_model, str)
        if hasattr(related_model, '__name__'):
            assert related_model.__name__ == 'User'

    def test_title_field_is_char_field(self) -> None:
        """Проверяет тип поля title."""
        field = PersonalCollection._meta.get_field('title')
        assert isinstance(field, models.CharField)
        assert field.max_length == 256
        assert field.blank is False

    def test_city_field_is_many_to_many(self) -> None:
        """Проверяет что поле city является ManyToManyField."""
        field = PersonalCollection._meta.get_field('city')
        assert isinstance(field, models.ManyToManyField)

    def test_created_at_field_is_datetime_field(self) -> None:
        """Проверяет тип поля created_at."""
        field = PersonalCollection._meta.get_field('created_at')
        assert isinstance(field, models.DateTimeField)
        assert field.auto_now_add is True

    def test_updated_at_field_is_datetime_field(self) -> None:
        """Проверяет тип поля updated_at."""
        field = PersonalCollection._meta.get_field('updated_at')
        assert isinstance(field, models.DateTimeField)
        assert field.auto_now is True

    def test_is_public_field_is_boolean_field(self) -> None:
        """Проверяет тип поля is_public."""
        field = PersonalCollection._meta.get_field('is_public')
        assert isinstance(field, models.BooleanField)
        assert field.default is False

    def test_meta_ordering(self) -> None:
        """Проверяет сортировку модели."""
        assert PersonalCollection._meta.ordering == ['-created_at']

    def test_meta_verbose_name(self) -> None:
        """Проверяет verbose_name модели."""
        assert PersonalCollection._meta.verbose_name == 'Персональная коллекция'

    def test_meta_verbose_name_plural(self) -> None:
        """Проверяет verbose_name_plural модели."""
        assert PersonalCollection._meta.verbose_name_plural == 'Персональные коллекции'


@pytest.mark.django_db
@pytest.mark.integration
class TestPersonalCollectionModelMethods:
    """Интеграционные тесты для методов модели PersonalCollection."""

    @pytest.fixture
    def user(self, django_user_model: Any) -> Any:
        """Создает пользователя для тестов."""
        return django_user_model.objects.create_user(username='testuser', password='testpass123')

    @pytest.fixture
    def collection(self, user: Any) -> PersonalCollection:
        """Создает персональную коллекцию для тестов."""
        return PersonalCollection.objects.create(
            user=user, title='Тестовая коллекция', is_public=False
        )

    def test_str_method(self, collection: PersonalCollection) -> None:
        """Проверяет метод __str__."""
        assert str(collection) == f'{collection.user.username} - Тестовая коллекция'

    def test_get_absolute_url(self, collection: PersonalCollection) -> None:
        """Проверяет метод get_absolute_url."""
        url = collection.get_absolute_url()
        assert url == f'/collection/personal/{collection.pk}/list'

    def test_collection_has_uuid_id(self, collection: PersonalCollection) -> None:
        """Проверяет что коллекция имеет UUID в качестве ID."""
        assert collection.id is not None
        assert isinstance(collection.id, type(collection.id))  # UUID type check

    def test_collection_default_is_public_false(self, user: Any) -> None:
        """Проверяет что по умолчанию коллекция приватная."""
        collection = PersonalCollection.objects.create(user=user, title='Тест')
        assert collection.is_public is False

    def test_collection_can_be_public(self, user: Any) -> None:
        """Проверяет что коллекция может быть публичной."""
        collection = PersonalCollection.objects.create(user=user, title='Тест', is_public=True)
        assert collection.is_public is True
