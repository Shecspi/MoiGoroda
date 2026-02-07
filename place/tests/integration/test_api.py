"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from django.urls import reverse
from rest_framework import status

from place.models import TagOSM, Category, Place, PlaceCollection


# ===== Тесты для GetCategory =====


@pytest.mark.integration
@pytest.mark.django_db
def test_get_category_list_authenticated(api_client: Any, django_user_model: Any) -> None:
    """Тест получения списка категорий авторизованным пользователем"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    Category.objects.create(name='Кафе')
    Category.objects.create(name='Музей')

    url = reverse('category_of_place')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]['name'] in ['Кафе', 'Музей']
    assert response.data[1]['name'] in ['Кафе', 'Музей']


@pytest.mark.integration
@pytest.mark.django_db
def test_get_category_list_unauthenticated(api_client: Any) -> None:
    """Тест что неавторизованный пользователь не может получить список категорий"""
    Category.objects.create(name='Кафе')

    url = reverse('category_of_place')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.django_db
def test_get_category_list_with_tags(api_client: Any, django_user_model: Any) -> None:
    """Тест получения списка категорий с тегами"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    tag1 = TagOSM.objects.create(name='amenity')
    tag2 = TagOSM.objects.create(name='cafe')

    category = Category.objects.create(name='Кафе')
    category.tags.add(tag1, tag2)

    url = reverse('category_of_place')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Кафе'
    assert len(response.data[0]['tags_detail']) == 2


@pytest.mark.integration
@pytest.mark.django_db
def test_get_category_list_sorted_by_name(api_client: Any, django_user_model: Any) -> None:
    """Тест что категории отсортированы по имени"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    Category.objects.create(name='Музей')
    Category.objects.create(name='Кафе')
    Category.objects.create(name='Ресторан')

    url = reverse('category_of_place')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    assert response.data[0]['name'] == 'Кафе'
    assert response.data[1]['name'] == 'Музей'
    assert response.data[2]['name'] == 'Ресторан'


# ===== Тесты для GetPlaces =====


@pytest.mark.integration
@pytest.mark.django_db
def test_get_places_list_authenticated(api_client: Any, django_user_model: Any) -> None:
    """Тест получения списка мест авторизованным пользователем"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    category = Category.objects.create(name='Кафе')

    Place.objects.create(
        name='Кафе 1',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    Place.objects.create(
        name='Кафе 2',
        latitude=56.7558,
        longitude=38.6173,
        category=category,
        user=user,
    )

    url = reverse('get_places')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.integration
@pytest.mark.django_db
def test_get_places_list_unauthenticated(api_client: Any) -> None:
    """Тест что неавторизованный пользователь не может получить список мест"""
    url = reverse('get_places')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.django_db
def test_get_places_list_only_own_places(api_client: Any, django_user_model: Any) -> None:
    """Тест что пользователь видит только свои места"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    api_client.force_authenticate(user=user1)

    category = Category.objects.create(name='Кафе')

    Place.objects.create(
        name='Место пользователя 1',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user1,
    )

    Place.objects.create(
        name='Место пользователя 2',
        latitude=56.7558,
        longitude=38.6173,
        category=category,
        user=user2,
    )

    url = reverse('get_places')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Место пользователя 1'


@pytest.mark.integration
@pytest.mark.django_db
def test_get_places_list_empty(api_client: Any, django_user_model: Any) -> None:
    """Тест получения пустого списка мест"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    url = reverse('get_places')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_get_places_public_collection_unauthenticated(
    api_client: Any, django_user_model: Any
) -> None:
    """Неавторизованный пользователь получает места из публичной коллекции"""
    owner = django_user_model.objects.create_user(username='owner', password='pass')
    category = Category.objects.create(name='Кафе')
    collection = PlaceCollection.objects.create(
        user=owner, title='Публичная коллекция', is_public=True
    )
    Place.objects.create(
        name='Место в публичной коллекции',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=owner,
        collection=collection,
    )

    url = reverse('get_places') + f'?collection={collection.id}'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Место в публичной коллекции'


@pytest.mark.integration
@pytest.mark.django_db
def test_get_places_private_collection_unauthenticated(
    api_client: Any, django_user_model: Any
) -> None:
    """Неавторизованный пользователь получает пустой список при запросе приватной коллекции"""
    owner = django_user_model.objects.create_user(username='owner', password='pass')
    category = Category.objects.create(name='Кафе')
    collection = PlaceCollection.objects.create(
        user=owner, title='Приватная коллекция', is_public=False
    )
    Place.objects.create(
        name='Место в приватной коллекции',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=owner,
        collection=collection,
    )

    url = reverse('get_places') + f'?collection={collection.id}'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_get_places_public_collection_authenticated_other_user(
    api_client: Any, django_user_model: Any
) -> None:
    """Авторизованный пользователь получает места из чужой публичной коллекции"""
    owner = django_user_model.objects.create_user(username='owner', password='pass')
    other = django_user_model.objects.create_user(username='other', password='pass')
    api_client.force_authenticate(user=other)

    category = Category.objects.create(name='Кафе')
    collection = PlaceCollection.objects.create(
        user=owner, title='Публичная коллекция', is_public=True
    )
    Place.objects.create(
        name='Место владельца',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=owner,
        collection=collection,
    )

    url = reverse('get_places') + f'?collection={collection.id}'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Место владельца'


@pytest.mark.integration
@pytest.mark.django_db
def test_get_places_private_collection_authenticated_other_user(
    api_client: Any, django_user_model: Any
) -> None:
    """Авторизованный пользователь получает пустой список при запросе чужой приватной коллекции"""
    owner = django_user_model.objects.create_user(username='owner', password='pass')
    other = django_user_model.objects.create_user(username='other', password='pass')
    api_client.force_authenticate(user=other)

    category = Category.objects.create(name='Кафе')
    collection = PlaceCollection.objects.create(
        user=owner, title='Приватная коллекция', is_public=False
    )
    Place.objects.create(
        name='Место владельца',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=owner,
        collection=collection,
    )

    url = reverse('get_places') + f'?collection={collection.id}'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_get_places_visited_only_filter(api_client: Any, django_user_model: Any) -> None:
    """При visited_only=true возвращаются только посещённые места (для карты городов)"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    category = Category.objects.create(name='Кафе')

    Place.objects.create(
        name='Посещённое место',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
        is_visited=True,
    )
    Place.objects.create(
        name='Непосещённое место',
        latitude=56.7558,
        longitude=38.6173,
        category=category,
        user=user,
        is_visited=False,
    )

    url = reverse('get_places') + '?visited_only=true'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Посещённое место'


# ===== Тесты для CreatePlace =====


@pytest.mark.integration
@pytest.mark.django_db
def test_create_place_authenticated(api_client: Any, django_user_model: Any) -> None:
    """Тест создания места авторизованным пользователем"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    category = Category.objects.create(name='Кафе')

    url = reverse('create_place')
    data = {
        'name': 'Новое место',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'category': category.id,
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == 'Новое место'
    assert response.data['latitude'] == 55.7558
    assert response.data['longitude'] == 37.6173

    # Проверяем, что место создано в БД
    assert Place.objects.filter(name='Новое место').exists()
    place = Place.objects.get(name='Новое место')
    assert place.user == user
    assert place.is_visited is True  # default


@pytest.mark.integration
@pytest.mark.django_db
def test_create_place_unauthenticated(api_client: Any) -> None:
    """Тест что неавторизованный пользователь не может создать место"""
    category = Category.objects.create(name='Кафе')

    url = reverse('create_place')
    data = {
        'name': 'Новое место',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'category': category.id,
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Place.objects.filter(name='Новое место').exists()


@pytest.mark.integration
@pytest.mark.django_db
def test_create_place_with_invalid_data(api_client: Any, django_user_model: Any) -> None:
    """Тест создания места с невалидными данными"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    url = reverse('create_place')
    data = {
        'name': '',  # Пустое имя
        'latitude': 55.7558,
        'longitude': 37.6173,
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'name' in response.data


@pytest.mark.integration
@pytest.mark.django_db
def test_create_place_without_category(api_client: Any, django_user_model: Any) -> None:
    """Тест создания места без категории"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    url = reverse('create_place')
    data = {
        'name': 'Новое место',
        'latitude': 55.7558,
        'longitude': 37.6173,
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'category' in response.data


@pytest.mark.integration
@pytest.mark.django_db
def test_create_place_with_category_detail(api_client: Any, django_user_model: Any) -> None:
    """Тест что при создании места возвращается информация о категории"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    category = Category.objects.create(name='Кафе')

    url = reverse('create_place')
    data = {
        'name': 'Новое место',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'category': category.id,
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert 'category_detail' in response.data
    assert response.data['category_detail']['name'] == 'Кафе'


# ===== Тесты для UpdatePlace =====


@pytest.mark.integration
@pytest.mark.django_db
def test_update_place_authenticated(api_client: Any, django_user_model: Any) -> None:
    """Тест обновления места авторизованным пользователем"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    category1 = Category.objects.create(name='Кафе')
    category2 = Category.objects.create(name='Музей')

    place = Place.objects.create(
        name='Старое название',
        latitude=55.7558,
        longitude=37.6173,
        category=category1,
        user=user,
    )

    url = reverse('update_place', kwargs={'pk': place.id})
    data = {
        'name': 'Новое название',
        'category': category2.id,
    }

    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Новое название'

    # Проверяем, что место обновлено в БД
    place.refresh_from_db()
    assert place.name == 'Новое название'
    assert place.category == category2


@pytest.mark.integration
@pytest.mark.django_db
def test_update_place_unauthenticated(api_client: Any, django_user_model: Any) -> None:
    """Тест что неавторизованный пользователь не может обновить место"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Место',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    url = reverse('update_place', kwargs={'pk': place.id})
    data = {'name': 'Новое название'}

    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.django_db
def test_update_place_other_user(api_client: Any, django_user_model: Any) -> None:
    """Тест что пользователь не может обновить чужое место"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    api_client.force_authenticate(user=user2)

    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Место пользователя 1',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user1,
    )

    url = reverse('update_place', kwargs={'pk': place.id})
    data = {'name': 'Взломанное место'}

    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Проверяем, что место не изменилось
    place.refresh_from_db()
    assert place.name == 'Место пользователя 1'


@pytest.mark.integration
@pytest.mark.django_db
def test_update_place_only_name(api_client: Any, django_user_model: Any) -> None:
    """Тест обновления только названия места"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Старое название',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    original_latitude = place.latitude
    original_longitude = place.longitude

    url = reverse('update_place', kwargs={'pk': place.id})
    data = {'name': 'Новое название'}

    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK

    # Проверяем, что координаты не изменились
    place.refresh_from_db()
    assert place.latitude == original_latitude
    assert place.longitude == original_longitude


@pytest.mark.integration
@pytest.mark.django_db
def test_update_place_only_category(api_client: Any, django_user_model: Any) -> None:
    """Тест обновления только категории места"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    category1 = Category.objects.create(name='Кафе')
    category2 = Category.objects.create(name='Музей')

    place = Place.objects.create(
        name='Место',
        latitude=55.7558,
        longitude=37.6173,
        category=category1,
        user=user,
    )

    original_name = place.name

    url = reverse('update_place', kwargs={'pk': place.id})
    data = {'category': category2.id}

    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK

    # Проверяем, что название не изменилось
    place.refresh_from_db()
    assert place.name == original_name
    assert place.category == category2


# ===== Тесты для DeletePlace =====


@pytest.mark.integration
@pytest.mark.django_db
def test_delete_place_authenticated(api_client: Any, django_user_model: Any) -> None:
    """Тест удаления места авторизованным пользователем"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Место для удаления',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    url = reverse('delete_place', kwargs={'pk': place.id})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Place.objects.filter(id=place.id).exists()


@pytest.mark.integration
@pytest.mark.django_db
def test_delete_place_unauthenticated(api_client: Any, django_user_model: Any) -> None:
    """Тест что неавторизованный пользователь не может удалить место"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Место',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
    )

    url = reverse('delete_place', kwargs={'pk': place.id})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Place.objects.filter(id=place.id).exists()


@pytest.mark.integration
@pytest.mark.django_db
def test_delete_place_other_user(api_client: Any, django_user_model: Any) -> None:
    """Тест что пользователь не может удалить чужое место"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    api_client.force_authenticate(user=user2)

    category = Category.objects.create(name='Кафе')

    place = Place.objects.create(
        name='Место пользователя 1',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user1,
    )

    url = reverse('delete_place', kwargs={'pk': place.id})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Place.objects.filter(id=place.id).exists()


# ===== Тесты для GetPlaceCollections =====


@pytest.mark.integration
@pytest.mark.django_db
def test_get_place_collections_authenticated(api_client: Any, django_user_model: Any) -> None:
    """Тест получения списка коллекций мест авторизованным пользователем"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    PlaceCollection.objects.create(user=user, title='Коллекция 1', is_public=False)
    PlaceCollection.objects.create(user=user, title='Коллекция 2', is_public=True)

    url = reverse('get_place_collections')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    titles = [c['title'] for c in response.data]
    assert 'Коллекция 1' in titles
    assert 'Коллекция 2' in titles


@pytest.mark.integration
@pytest.mark.django_db
def test_get_place_collections_unauthenticated(api_client: Any) -> None:
    """Тест что неавторизованный пользователь не получает список коллекций"""
    url = reverse('get_place_collections')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.django_db
def test_get_place_collections_only_own(api_client: Any, django_user_model: Any) -> None:
    """Тест что возвращаются только коллекции текущего пользователя"""
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')
    api_client.force_authenticate(user=user1)

    PlaceCollection.objects.create(user=user1, title='Моя', is_public=False)
    PlaceCollection.objects.create(user=user2, title='Чужая', is_public=True)

    url = reverse('get_place_collections')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['title'] == 'Моя'


# ===== Тесты для CreatePlaceCollection =====


@pytest.mark.integration
@pytest.mark.django_db
def test_create_place_collection_authenticated(api_client: Any, django_user_model: Any) -> None:
    """Тест создания коллекции мест авторизованным пользователем"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    url = reverse('create_place_collection')
    data = {'title': 'Новая коллекция', 'is_public': True}
    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == 'Новая коллекция'
    assert response.data['is_public'] is True
    assert PlaceCollection.objects.filter(title='Новая коллекция', user=user).exists()


@pytest.mark.integration
@pytest.mark.django_db
def test_create_place_collection_unauthenticated(api_client: Any) -> None:
    """Тест что неавторизованный пользователь не может создать коллекцию"""
    url = reverse('create_place_collection')
    data = {'title': 'Коллекция', 'is_public': False}
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.django_db
def test_update_place_collection_user_read_only(api_client: Any, django_user_model: Any) -> None:
    """Тест что PATCH коллекции с полем user не меняет владельца (user — read_only)"""
    owner = django_user_model.objects.create_user(username='owner', password='pass')
    other = django_user_model.objects.create_user(username='other', password='pass')
    api_client.force_authenticate(user=owner)

    collection = PlaceCollection.objects.create(user=owner, title='Моя коллекция', is_public=False)

    url = reverse('update_place_collection', kwargs={'pk': collection.id})
    data = {'title': 'Новое название', 'user': other.id}

    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'Новое название'
    collection.refresh_from_db()
    assert collection.user_id == owner.id
    assert collection.user_id != other.id


# ===== Тесты для Place с is_visited и collection =====


@pytest.mark.integration
@pytest.mark.django_db
def test_create_place_with_is_visited_and_collection(
    api_client: Any, django_user_model: Any
) -> None:
    """Тест создания места с is_visited и коллекцией"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    category = Category.objects.create(name='Кафе')
    collection = PlaceCollection.objects.create(user=user, title='Избранное', is_public=False)

    url = reverse('create_place')
    data = {
        'name': 'Место в коллекции',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'category': category.id,
        'is_visited': False,
        'collection': collection.id,
    }
    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['is_visited'] is False
    assert response.data['collection_detail'] is not None
    assert response.data['collection_detail']['title'] == 'Избранное'
    place = Place.objects.get(name='Место в коллекции')
    assert place.is_visited is False
    assert place.collection_id == collection.id


@pytest.mark.integration
@pytest.mark.django_db
def test_update_place_is_visited_and_collection(api_client: Any, django_user_model: Any) -> None:
    """Тест обновления is_visited и collection места"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    category = Category.objects.create(name='Кафе')
    collection = PlaceCollection.objects.create(user=user, title='Коллекция', is_public=False)
    place = Place.objects.create(
        name='Место',
        latitude=55.7558,
        longitude=37.6173,
        category=category,
        user=user,
        is_visited=True,
        collection=None,
    )

    url = reverse('update_place', kwargs={'pk': place.id})
    data = {'is_visited': False, 'collection': collection.id}
    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    place.refresh_from_db()
    assert place.is_visited is False
    assert place.collection_id == collection.id


@pytest.mark.integration
@pytest.mark.django_db
def test_delete_nonexistent_place(api_client: Any, django_user_model: Any) -> None:
    """Тест удаления несуществующего места"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    url = reverse('delete_place', kwargs={'pk': 99999})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
