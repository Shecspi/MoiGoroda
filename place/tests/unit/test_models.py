"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from django.db import models


@pytest.mark.unit
def test_tag_osm_meta_verbose_name() -> None:
    """Тест verbose_name модели TagOSM"""
    from place.models import TagOSM

    assert TagOSM._meta.verbose_name == 'Тег'
    assert TagOSM._meta.verbose_name_plural == 'Теги'


@pytest.mark.unit
def test_tag_osm_field_types() -> None:
    """Тест типов полей модели TagOSM"""
    from place.models import TagOSM

    # Проверяем типы полей
    assert isinstance(TagOSM._meta.get_field('name'), models.CharField)
    name_field = TagOSM._meta.get_field('name')
    assert name_field.max_length == 255
    assert name_field.blank is False
    assert name_field.null is False
    assert name_field.unique is False


@pytest.mark.unit
def test_tag_osm_str_method() -> None:
    """Тест строкового представления модели TagOSM"""
    from place.models import TagOSM

    tag = TagOSM(name='amenity')
    assert str(tag) == 'amenity'


@pytest.mark.unit
def test_category_meta_verbose_name() -> None:
    """Тест verbose_name модели Category"""
    from place.models import Category

    assert Category._meta.verbose_name == 'Категория'
    assert Category._meta.verbose_name_plural == 'Категории'


@pytest.mark.unit
def test_category_field_types() -> None:
    """Тест типов полей модели Category"""
    from place.models import Category

    # Проверяем типы полей
    assert isinstance(Category._meta.get_field('name'), models.CharField)
    assert isinstance(Category._meta.get_field('tags'), models.ManyToManyField)

    name_field = Category._meta.get_field('name')
    assert name_field.max_length == 255
    assert name_field.blank is False
    assert name_field.null is False
    assert name_field.unique is False

    tags_field = Category._meta.get_field('tags')
    assert tags_field.blank is True


@pytest.mark.unit
def test_category_str_method() -> None:
    """Тест строкового представления модели Category"""
    from place.models import Category

    category = Category(name='Кафе')
    assert str(category) == 'Кафе'


@pytest.mark.unit
def test_place_meta_verbose_name() -> None:
    """Тест verbose_name модели Place"""
    from place.models import Place

    assert Place._meta.verbose_name == 'Интересное место'
    assert Place._meta.verbose_name_plural == 'Интересные места'


@pytest.mark.unit
def test_place_field_types() -> None:
    """Тест типов полей модели Place"""
    from place.models import Place

    # Проверяем типы полей
    assert isinstance(Place._meta.get_field('name'), models.CharField)
    assert isinstance(Place._meta.get_field('latitude'), models.FloatField)
    assert isinstance(Place._meta.get_field('longitude'), models.FloatField)
    assert isinstance(Place._meta.get_field('category'), models.ForeignKey)
    assert isinstance(Place._meta.get_field('created_at'), models.DateTimeField)
    assert isinstance(Place._meta.get_field('updated_at'), models.DateTimeField)
    assert isinstance(Place._meta.get_field('user'), models.ForeignKey)
    assert isinstance(Place._meta.get_field('is_visited'), models.BooleanField)
    assert isinstance(Place._meta.get_field('collection'), models.ForeignKey)

    # Проверяем параметры полей
    name_field = Place._meta.get_field('name')
    assert name_field.max_length == 255
    assert name_field.blank is False
    assert name_field.null is False
    assert name_field.unique is False

    latitude_field = Place._meta.get_field('latitude')
    assert latitude_field.blank is False
    assert latitude_field.null is False
    assert latitude_field.unique is False

    longitude_field = Place._meta.get_field('longitude')
    assert longitude_field.blank is False
    assert longitude_field.null is False
    assert longitude_field.unique is False

    created_at_field = Place._meta.get_field('created_at')
    assert created_at_field.auto_now_add is True

    updated_at_field = Place._meta.get_field('updated_at')
    assert updated_at_field.auto_now is True

    category_field = Place._meta.get_field('category')
    # Проверяем, что это ForeignKey
    assert isinstance(category_field, models.ForeignKey)

    user_field = Place._meta.get_field('user')
    # Проверяем, что это ForeignKey
    assert isinstance(user_field, models.ForeignKey)

    is_visited_field = Place._meta.get_field('is_visited')
    assert is_visited_field.default is True

    collection_field = Place._meta.get_field('collection')
    assert collection_field.null is True
    assert collection_field.blank is True


@pytest.mark.unit
def test_place_model_ordering() -> None:
    """Тест сортировки модели Place"""
    from place.models import Place

    # Проверяем, что модель имеет правильный ordering (если есть)
    # По умолчанию ordering не установлен
    assert Place._meta.ordering == []


@pytest.mark.unit
def test_place_model_has_timestamps() -> None:
    """Тест наличия полей с временными метками в модели Place"""
    from place.models import Place

    assert hasattr(Place, 'created_at')
    assert hasattr(Place, 'updated_at')


@pytest.mark.unit
def test_category_has_tags_relation() -> None:
    """Тест наличия связи many-to-many с тегами в модели Category"""
    from place.models import Category

    assert hasattr(Category, 'tags')
    tags_field = Category._meta.get_field('tags')
    assert tags_field.many_to_many is True


# ===== Тесты для PlaceCollection =====


@pytest.mark.unit
def test_place_collection_meta_verbose_name() -> None:
    """Тест verbose_name модели PlaceCollection"""
    from place.models import PlaceCollection

    assert PlaceCollection._meta.verbose_name == 'Коллекция мест'
    assert PlaceCollection._meta.verbose_name_plural == 'Коллекции мест'


@pytest.mark.unit
@pytest.mark.django_db
def test_place_collection_str_method(django_user_model: Any) -> None:
    """Тест строкового представления PlaceCollection"""
    from place.models import PlaceCollection

    user = django_user_model.objects.create_user(username='testuser', password='password123')
    collection = PlaceCollection.objects.create(user=user, title='Избранное', is_public=False)
    assert str(collection) == 'testuser - Избранное'


@pytest.mark.unit
def test_place_collection_has_created_at_updated_at() -> None:
    """Тест наличия полей created_at и updated_at в PlaceCollection"""
    from place.models import PlaceCollection

    assert hasattr(PlaceCollection, 'created_at')
    assert hasattr(PlaceCollection, 'updated_at')
    assert isinstance(PlaceCollection._meta.get_field('created_at'), models.DateTimeField)
    assert isinstance(PlaceCollection._meta.get_field('updated_at'), models.DateTimeField)
