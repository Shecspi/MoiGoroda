"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any

from place.models import TagOSM, Category, Place


@pytest.mark.integration
@pytest.mark.django_db
def test_tag_osm_create() -> None:
    """Тест создания TagOSM"""
    tag = TagOSM.objects.create(name='amenity')
    assert tag.id is not None
    assert tag.name == 'amenity'
    assert str(tag) == 'amenity'


@pytest.mark.integration
@pytest.mark.django_db
def test_tag_osm_unique_name_not_required() -> None:
    """Тест что имя тега не должно быть уникальным"""
    TagOSM.objects.create(name='amenity')
    tag2 = TagOSM.objects.create(name='amenity')
    assert tag2.id is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_category_create() -> None:
    """Тест создания Category"""
    category = Category.objects.create(name='Кафе')
    assert category.id is not None
    assert category.name == 'Кафе'
    assert str(category) == 'Кафе'


@pytest.mark.integration
@pytest.mark.django_db
def test_category_with_tags() -> None:
    """Тест создания Category с тегами"""
    tag1 = TagOSM.objects.create(name='amenity')
    tag2 = TagOSM.objects.create(name='cafe')

    category = Category.objects.create(name='Кафе')
    category.tags.add(tag1, tag2)

    assert category.tags.count() == 2
    assert tag1 in category.tags.all()
    assert tag2 in category.tags.all()


@pytest.mark.integration
@pytest.mark.django_db
def test_category_can_have_no_tags() -> None:
    """Тест что Category может существовать без тегов"""
    category = Category.objects.create(name='Кафе')
    assert category.tags.count() == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_place_create(django_user_model: Any) -> None:
    """Тест создания Place"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Кафе "Уютное"',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    assert place.id is not None
    assert place.name == 'Кафе "Уютное"'
    assert place.latitude == 55.7558
    assert place.longitude == 37.6173
    assert place.category == category
    assert place.user == user


@pytest.mark.integration
@pytest.mark.django_db
def test_place_has_created_at(django_user_model: Any) -> None:
    """Тест что Place имеет поле created_at"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Кафе "Уютное"',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    assert place.created_at is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_place_has_updated_at(django_user_model: Any) -> None:
    """Тест что Place имеет поле updated_at"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Кафе "Уютное"',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    assert place.updated_at is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_place_updated_at_changes_on_update(django_user_model: Any) -> None:
    """Тест что updated_at изменяется при обновлении"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Кафе "Уютное"',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    original_updated_at = place.updated_at

    # Небольшая задержка для гарантии изменения времени
    import time

    time.sleep(0.1)

    place.name = 'Кафе "Новое"'
    place.save()

    place.refresh_from_db()
    assert place.updated_at > original_updated_at


@pytest.mark.integration
@pytest.mark.django_db
def test_place_cascade_delete_category_protected(django_user_model: Any) -> None:
    """Тест что нельзя удалить Category, если есть связанные Place"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    Place.objects.create(
        name='Кафе "Уютное"',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    # Попытка удалить категорию должна вызвать ProtectedError
    with pytest.raises(Exception):  # django.db.models.deletion.ProtectedError
        category.delete()


@pytest.mark.integration
@pytest.mark.django_db
def test_place_cascade_delete_user_protected(django_user_model: Any) -> None:
    """Тест что нельзя удалить User, если есть связанные Place"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    Place.objects.create(
        name='Кафе "Уютное"',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    # Попытка удалить пользователя должна вызвать ProtectedError
    with pytest.raises(Exception):  # django.db.models.deletion.ProtectedError
        user.delete()


@pytest.mark.integration
@pytest.mark.django_db
def test_place_filter_by_user(django_user_model: Any) -> None:
    """Тест фильтрации Place по пользователю"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    category = Category.objects.create(name='Кафе')

    place1 = Place.objects.create(
        name='Место 1',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user1,
    )

    place2 = Place.objects.create(
        name='Место 2',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user2,
    )

    user1_places = Place.objects.filter(user=user1)
    assert user1_places.count() == 1
    assert place1 in user1_places

    user2_places = Place.objects.filter(user=user2)
    assert user2_places.count() == 1
    assert place2 in user2_places


@pytest.mark.integration
@pytest.mark.django_db
def test_place_filter_by_category(django_user_model: Any) -> None:
    """Тест фильтрации Place по категории"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category1 = Category.objects.create(name='Кафе')
    category2 = Category.objects.create(name='Музей')

    place1 = Place.objects.create(
        name='Кафе',
        latitude=55.7558,
        longitude=37.6173,
        category=category1,
        user=user,
    )

    place2 = Place.objects.create(
        name='Музей',
        latitude=55.7558,
        longitude=37.6173,
        category=category2,
        user=user,
    )

    cafe_places = Place.objects.filter(category=category1)
    assert cafe_places.count() == 1
    assert place1 in cafe_places

    museum_places = Place.objects.filter(category=category2)
    assert museum_places.count() == 1
    assert place2 in museum_places


@pytest.mark.integration
@pytest.mark.django_db
def test_multiple_places_same_user(django_user_model: Any) -> None:
    """Тест что пользователь может иметь несколько мест"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    place1 = Place.objects.create(
        name='Место 1',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    place2 = Place.objects.create(
        name='Место 2',
        latitude=56.7558,
        longitude=38.6173,
        category=category,
        user=user,
    )

    user_places = Place.objects.filter(user=user)
    assert user_places.count() == 2
    assert place1 in user_places
    assert place2 in user_places


@pytest.mark.integration
@pytest.mark.django_db
def test_category_can_have_multiple_places(django_user_model: Any) -> None:
    """Тест что категория может иметь несколько мест"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    place1 = Place.objects.create(
        name='Кафе 1',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    place2 = Place.objects.create(
        name='Кафе 2',
        latitude=56.7558,
        longitude=38.6173,
        category=category,
        user=user,
    )

    category_places = Place.objects.filter(category=category)
    assert category_places.count() == 2
    assert place1 in category_places
    assert place2 in category_places


@pytest.mark.integration
@pytest.mark.django_db
def test_tag_can_be_used_by_multiple_categories() -> None:
    """Тест что тег может использоваться несколькими категориями"""
    tag = TagOSM.objects.create(name='amenity')

    category1 = Category.objects.create(name='Кафе')
    category1.tags.add(tag)

    category2 = Category.objects.create(name='Ресторан')
    category2.tags.add(tag)

    assert tag in category1.tags.all()
    assert tag in category2.tags.all()


@pytest.mark.integration
@pytest.mark.django_db
def test_category_can_have_multiple_tags() -> None:
    """Тест что категория может иметь несколько тегов"""
    tag1 = TagOSM.objects.create(name='amenity')
    tag2 = TagOSM.objects.create(name='cafe')
    tag3 = TagOSM.objects.create(name='food')

    category = Category.objects.create(name='Кафе')
    category.tags.add(tag1, tag2, tag3)

    assert category.tags.count() == 3
    assert tag1 in category.tags.all()
    assert tag2 in category.tags.all()
    assert tag3 in category.tags.all()


@pytest.mark.integration
@pytest.mark.django_db
def test_place_update_name(django_user_model: Any) -> None:
    """Тест обновления названия места"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Старое название',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    place.name = 'Новое название'
    place.save()

    place.refresh_from_db()
    assert place.name == 'Новое название'


@pytest.mark.integration
@pytest.mark.django_db
def test_place_update_category(django_user_model: Any) -> None:
    """Тест обновления категории места"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category1 = Category.objects.create(name='Кафе')
    category2 = Category.objects.create(name='Музей')

    place = Place.objects.create(
        name='Место',
        latitude=55.7558,
        longitude=37.6173,
        category=category1,
        user=user,
    )

    place.category = category2
    place.save()

    place.refresh_from_db()
    assert place.category == category2


@pytest.mark.integration
@pytest.mark.django_db
def test_place_update_coordinates(django_user_model: Any) -> None:
    """Тест обновления координат места"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Место',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    place.latitude = 56.7558
    place.longitude = 38.6173
    place.save()

    place.refresh_from_db()
    assert place.latitude == 56.7558
    assert place.longitude == 38.6173


@pytest.mark.integration
@pytest.mark.django_db
def test_place_delete(django_user_model: Any) -> None:
    """Тест удаления места"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Место',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    place_id = place.id
    place.delete()

    assert not Place.objects.filter(id=place_id).exists()


@pytest.mark.integration
@pytest.mark.django_db
def test_category_delete_without_places() -> None:
    """Тест удаления категории без связанных мест"""
    category = Category.objects.create(name='Кафе')
    category_id = category.id

    category.delete()

    assert not Category.objects.filter(id=category_id).exists()


@pytest.mark.integration
@pytest.mark.django_db
def test_tag_delete_removes_from_categories() -> None:
    """Тест что удаление тега удаляет его из категорий"""
    tag = TagOSM.objects.create(name='amenity')
    category = Category.objects.create(name='Кафе')
    category.tags.add(tag)

    assert tag in category.tags.all()

    tag.delete()

    category.refresh_from_db()
    assert tag not in category.tags.all()
