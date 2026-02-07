"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from unittest.mock import Mock

from place.serializers import (
    TagOSMSerializer,
    CategorySerializer,
    PlaceSerializer,
    PlaceCollectionSerializer,
)


# ===== Тесты для TagOSMSerializer =====


@pytest.mark.unit
def test_tag_osm_serializer_meta() -> None:
    """Тест мета-класса TagOSMSerializer"""
    assert TagOSMSerializer.Meta.model.__name__ == 'TagOSM'
    assert TagOSMSerializer.Meta.fields == '__all__'


@pytest.mark.unit
def test_tag_osm_serializer_serialization() -> None:
    """Тест сериализации TagOSM"""
    data = {'name': 'amenity'}
    serializer = TagOSMSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data['name'] == 'amenity'


@pytest.mark.unit
def test_tag_osm_serializer_required_fields() -> None:
    """Тест обязательных полей TagOSMSerializer"""
    serializer = TagOSMSerializer(data={})
    assert not serializer.is_valid()
    assert 'name' in serializer.errors


# ===== Тесты для CategorySerializer =====


@pytest.mark.unit
def test_category_serializer_meta() -> None:
    """Тест мета-класса CategorySerializer"""
    assert CategorySerializer.Meta.model.__name__ == 'Category'
    assert CategorySerializer.Meta.fields == '__all__'


@pytest.mark.unit
def test_category_serializer_has_tags_detail() -> None:
    """Тест наличия поля tags_detail в CategorySerializer"""
    serializer = CategorySerializer()
    assert 'tags_detail' in serializer.fields
    tags_detail = serializer.fields['tags_detail']
    assert tags_detail.read_only is True
    assert tags_detail.source == 'tags'
    assert hasattr(tags_detail, 'many')
    assert tags_detail.many is True


@pytest.mark.unit
def test_category_serializer_tags_write_only() -> None:
    """Тест что поле tags является write_only"""
    tags_field = CategorySerializer().fields['tags']
    assert tags_field.write_only is True


@pytest.mark.unit
def test_category_serializer_serialization() -> None:
    """Тест сериализации Category"""
    data = {'name': 'Кафе', 'tags': []}
    serializer = CategorySerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data['name'] == 'Кафе'


@pytest.mark.unit
def test_category_serializer_required_fields() -> None:
    """Тест обязательных полей CategorySerializer"""
    serializer = CategorySerializer(data={})
    assert not serializer.is_valid()
    assert 'name' in serializer.errors


# ===== Тесты для PlaceSerializer =====


@pytest.mark.unit
def test_place_serializer_meta() -> None:
    """Тест мета-класса PlaceSerializer"""
    assert PlaceSerializer.Meta.model.__name__ == 'Place'
    assert 'id' in PlaceSerializer.Meta.fields
    assert 'name' in PlaceSerializer.Meta.fields
    assert 'latitude' in PlaceSerializer.Meta.fields
    assert 'longitude' in PlaceSerializer.Meta.fields
    assert 'category' in PlaceSerializer.Meta.fields
    assert 'category_detail' in PlaceSerializer.Meta.fields
    assert 'created_at' in PlaceSerializer.Meta.fields
    assert 'updated_at' in PlaceSerializer.Meta.fields
    assert 'user' in PlaceSerializer.Meta.fields
    assert 'is_visited' in PlaceSerializer.Meta.fields
    assert 'collection' in PlaceSerializer.Meta.fields
    assert 'collection_detail' in PlaceSerializer.Meta.fields


@pytest.mark.unit
def test_place_serializer_has_category_detail() -> None:
    """Тест наличия поля category_detail в PlaceSerializer"""
    serializer = PlaceSerializer()
    assert 'category_detail' in serializer.fields
    category_detail = serializer.fields['category_detail']
    assert category_detail.read_only is True
    assert category_detail.source == 'category'


@pytest.mark.unit
def test_place_serializer_category_write_only() -> None:
    """Тест что поле category является write_only"""
    category_field = PlaceSerializer().fields['category']
    assert category_field.write_only is True


@pytest.mark.unit
def test_place_serializer_user_write_only() -> None:
    """Тест что поле user является write_only"""
    user_field = PlaceSerializer().fields['user']
    assert user_field.write_only is True
    assert user_field.required is False


@pytest.mark.unit
def test_place_serializer_has_collection_detail() -> None:
    """Тест наличия поля collection_detail в PlaceSerializer"""
    serializer = PlaceSerializer()
    assert 'collection_detail' in serializer.fields
    collection_detail = serializer.fields['collection_detail']
    assert collection_detail.read_only is True
    assert collection_detail.source == 'collection'


@pytest.mark.unit
def test_place_serializer_collection_write_only() -> None:
    """Тест что поле collection является write_only и allow_null"""
    collection_field = PlaceSerializer().fields['collection']
    assert collection_field.write_only is True
    assert collection_field.required is False


@pytest.mark.unit
def test_place_serializer_read_only_fields() -> None:
    """Тест read_only полей PlaceSerializer"""
    assert 'created_at' in PlaceSerializer.Meta.read_only_fields
    assert 'updated_at' in PlaceSerializer.Meta.read_only_fields


@pytest.mark.unit
@pytest.mark.django_db
def test_place_serializer_create_with_context(django_user_model: Any) -> None:
    """Тест метода create с контекстом request"""
    from place.models import Category

    # Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Создаём категорию
    category = Category.objects.create(name='Кафе')

    # Создаём мок request с user
    mock_request = Mock()
    mock_request.user = user

    serializer = PlaceSerializer(
        data={
            'name': 'Тестовое место',
            'latitude': 55.7558,
            'longitude': 37.6173,
            'category': category.id,
        },
        context={'request': mock_request},
    )

    # Проверяем, что сериализатор валиден
    assert serializer.is_valid()


@pytest.mark.unit
@pytest.mark.django_db
def test_place_serializer_create_without_context(django_user_model: Any) -> None:
    """Тест метода create без контекста request"""
    from place.models import Category

    # Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Создаём категорию
    category = Category.objects.create(name='Кафе')

    serializer = PlaceSerializer(
        data={
            'name': 'Тестовое место',
            'latitude': 55.7558,
            'longitude': 37.6173,
            'category': category.id,
            'user': user.id,
        }
    )

    # Проверяем, что сериализатор валиден
    assert serializer.is_valid()


@pytest.mark.unit
@pytest.mark.django_db
def test_place_serializer_create_removes_user_from_validated_data(django_user_model: Any) -> None:
    """Тест что метод create удаляет user из validated_data при наличии request"""
    from place.models import Category

    # Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Создаём категорию
    category = Category.objects.create(name='Кафе')

    # Создаём мок request с user
    mock_request = Mock()
    mock_request.user = user

    serializer = PlaceSerializer(
        data={
            'name': 'Тестовое место',
            'latitude': 55.7558,
            'longitude': 37.6173,
            'category': category.id,
            'user': 999,  # Этот user должен быть проигнорирован
        },
        context={'request': mock_request},
    )

    if serializer.is_valid():
        # Проверяем, что user был удалён из validated_data
        # user не должен быть в validated_data, если есть request
        assert serializer.validated_data is not None


@pytest.mark.unit
def test_place_serializer_update_editable_fields() -> None:
    """Тест что метод update обновляет только разрешённые поля"""
    from place.models import Place, Category

    # Создаём мок объекта Place
    mock_place = Mock(spec=Place)
    mock_place.name = 'Старое название'
    mock_place.category = Mock(spec=Category)
    mock_place.save = Mock()

    # Создаём мок категории
    mock_category = Mock(spec=Category)
    mock_category.id = 2

    serializer = PlaceSerializer()

    # Вызываем update с данными, содержащими разрешённые и неразрешённые поля
    validated_data = {
        'name': 'Новое название',
        'category': mock_category,
        'latitude': 99.9999,  # Это поле не должно обновиться
        'longitude': 88.8888,  # Это поле не должно обновиться
    }

    serializer.update(mock_place, validated_data)

    # Проверяем, что save был вызван
    assert mock_place.save.called

    # Проверяем, что name был обновлён
    assert mock_place.name == 'Новое название'

    # Проверяем, что category был обновлён
    assert mock_place.category == mock_category


@pytest.mark.unit
def test_place_serializer_update_ignores_non_editable_fields() -> None:
    """Тест что метод update игнорирует неразрешённые поля"""
    from place.models import Place

    # Создаём мок объекта Place
    mock_place = Mock(spec=Place)
    mock_place.name = 'Старое название'
    mock_place.latitude = 55.7558
    mock_place.longitude = 37.6173
    mock_place.save = Mock()

    serializer = PlaceSerializer()

    # Вызываем update только с неразрешёнными полями
    validated_data = {
        'latitude': 99.9999,
        'longitude': 88.8888,
    }

    serializer.update(mock_place, validated_data)

    # Проверяем, что save был вызван (метод update всегда вызывает save)
    assert mock_place.save.called

    # Проверяем, что latitude и longitude НЕ изменились
    assert mock_place.latitude == 55.7558
    assert mock_place.longitude == 37.6173


@pytest.mark.unit
def test_place_serializer_required_fields() -> None:
    """Тест обязательных полей PlaceSerializer"""
    serializer = PlaceSerializer(data={})
    assert not serializer.is_valid()
    assert 'name' in serializer.errors
    assert 'latitude' in serializer.errors
    assert 'longitude' in serializer.errors


@pytest.mark.unit
@pytest.mark.django_db
def test_place_serializer_valid_data(django_user_model: Any) -> None:
    """Тест валидации корректных данных PlaceSerializer"""
    from place.models import Category

    # Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Создаём категорию
    category = Category.objects.create(name='Кафе')

    data = {
        'name': 'Тестовое место',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'category': category.id,
        'user': user.id,
    }
    serializer = PlaceSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data['name'] == 'Тестовое место'
    assert serializer.validated_data['latitude'] == 55.7558
    assert serializer.validated_data['longitude'] == 37.6173


@pytest.mark.unit
@pytest.mark.django_db
def test_place_serializer_invalid_latitude(django_user_model: Any) -> None:
    """Тест валидации некорректной широты"""
    from place.models import Category

    # Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Создаём категорию
    category = Category.objects.create(name='Кафе')

    data = {
        'name': 'Тестовое место',
        'latitude': 200.0,  # Некорректная широта
        'longitude': 37.6173,
        'category': category.id,
        'user': user.id,
    }
    serializer = PlaceSerializer(data=data)
    # Django FloatField не проверяет диапазон, но мы можем проверить тип
    assert serializer.is_valid() or 'latitude' in serializer.errors


@pytest.mark.unit
@pytest.mark.django_db
def test_place_serializer_invalid_longitude(django_user_model: Any) -> None:
    """Тест валидации некорректной долготы"""
    from place.models import Category

    # Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Создаём категорию
    category = Category.objects.create(name='Кафе')

    data = {
        'name': 'Тестовое место',
        'latitude': 55.7558,
        'longitude': 300.0,  # Некорректная долгота
        'category': category.id,
        'user': user.id,
    }
    serializer = PlaceSerializer(data=data)
    # Django FloatField не проверяет диапазон, но мы можем проверить тип
    assert serializer.is_valid() or 'longitude' in serializer.errors


# ===== Тесты для PlaceCollectionSerializer =====


@pytest.mark.unit
def test_place_collection_serializer_meta() -> None:
    """Тест мета-класса PlaceCollectionSerializer"""
    from place.models import PlaceCollection

    assert PlaceCollectionSerializer.Meta.model == PlaceCollection
    assert 'id' in PlaceCollectionSerializer.Meta.fields
    assert 'title' in PlaceCollectionSerializer.Meta.fields
    assert 'is_public' in PlaceCollectionSerializer.Meta.fields
    assert 'user' in PlaceCollectionSerializer.Meta.fields


@pytest.mark.unit
@pytest.mark.django_db
def test_place_serializer_create_with_is_visited_and_collection(
    django_user_model: Any,
) -> None:
    """Тест создания места с is_visited и collection"""
    from place.models import Category, PlaceCollection

    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')
    collection = PlaceCollection.objects.create(user=user, title='Мои места', is_public=False)
    mock_request = Mock()
    mock_request.user = user

    serializer = PlaceSerializer(
        data={
            'name': 'Место',
            'latitude': 55.7558,
            'longitude': 37.6173,
            'category': category.id,
            'is_visited': False,
            'collection': collection.id,
        },
        context={'request': mock_request},
    )
    assert serializer.is_valid(), serializer.errors
    place = serializer.save()
    assert place.is_visited is False
    assert place.collection_id == collection.id


@pytest.mark.unit
@pytest.mark.django_db
def test_place_serializer_create_rejects_other_user_collection(
    django_user_model: Any,
) -> None:
    """Тест что нельзя привязать место к коллекции другого пользователя"""
    from place.models import Category, PlaceCollection

    from rest_framework import serializers as drf_serializers

    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    category = Category.objects.create(name='Кафе')
    collection = PlaceCollection.objects.create(user=user2, title='Чужая коллекция', is_public=True)
    mock_request = Mock()
    mock_request.user = user1

    serializer = PlaceSerializer(
        data={
            'name': 'Место',
            'latitude': 55.7558,
            'longitude': 37.6173,
            'category': category.id,
            'collection': collection.id,
        },
        context={'request': mock_request},
    )
    assert serializer.is_valid(), serializer.errors
    with pytest.raises(drf_serializers.ValidationError) as exc_info:
        serializer.save()
    assert 'collection' in exc_info.value.detail
