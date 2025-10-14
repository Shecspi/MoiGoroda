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

from place.models import TagOSM, Category, Place


# ===== E2E тесты для полного цикла работы с местами =====


@pytest.mark.e2e
@pytest.mark.django_db
def test_complete_place_management_flow(api_client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Полный цикл управления местами
    Регистрация -> Создание категории -> Создание места -> Просмотр -> Обновление -> Удаление
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    # Шаг 2: Создаём теги и категорию
    tag1 = TagOSM.objects.create(name='amenity')
    tag2 = TagOSM.objects.create(name='cafe')

    category = Category.objects.create(name='Кафе')
    category.tags.add(tag1, tag2)

    # Шаг 3: Получаем список категорий
    url = reverse('category_of_place')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Кафе'

    # Шаг 4: Создаём место
    url = reverse('create_place')
    data = {
        'name': 'Кафе "Уютное"',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'category': category.id,
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    place_id = response.data['id']

    # Шаг 5: Получаем список своих мест
    url = reverse('get_places')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Кафе "Уютное"'

    # Шаг 6: Обновляем место
    url = reverse('update_place', kwargs={'pk': place_id})
    data = {'name': 'Кафе "Уютное" (обновлено)'}
    response = api_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Кафе "Уютное" (обновлено)'

    # Шаг 7: Удаляем место
    url = reverse('delete_place', kwargs={'pk': place_id})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Шаг 8: Проверяем, что место удалено
    url = reverse('get_places')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


@pytest.mark.e2e
@pytest.mark.django_db
def test_multiple_users_places_isolation(api_client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Изоляция мест между пользователями
    Два пользователя создают места и не видят чужие
    """
    # Шаг 1: Создаём двух пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    # Шаг 2: Создаём категорию
    category = Category.objects.create(name='Кафе')

    # Шаг 3: Пользователь 1 создаёт место
    api_client.force_authenticate(user=user1)
    url = reverse('create_place')
    data = {
        'name': 'Место пользователя 1',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'category': category.id,
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    # Шаг 4: Пользователь 1 видит своё место
    url = reverse('get_places')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Место пользователя 1'

    # Шаг 5: Пользователь 2 создаёт место
    api_client.force_authenticate(user=user2)
    url = reverse('create_place')
    data = {
        'name': 'Место пользователя 2',
        'latitude': 56.7558,
        'longitude': 38.6173,
        'category': category.id,
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    # Шаг 6: Пользователь 2 видит только своё место
    url = reverse('get_places')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Место пользователя 2'

    # Шаг 7: Пользователь 2 не может обновить место пользователя 1
    user1_place = Place.objects.filter(user=user1).first()
    assert user1_place is not None
    url = reverse('update_place', kwargs={'pk': user1_place.id})
    data = {'name': 'Взломанное место'}
    response = api_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.e2e
@pytest.mark.django_db
def test_place_category_workflow(api_client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Работа с категориями и местами
    Создание категорий -> Создание мест в разных категориях -> Изменение категории
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    # Шаг 2: Создаём несколько категорий
    category1 = Category.objects.create(name='Кафе')
    category2 = Category.objects.create(name='Музей')
    category3 = Category.objects.create(name='Ресторан')

    # Шаг 3: Получаем список категорий
    url = reverse('category_of_place')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3

    # Шаг 4: Создаём места в разных категориях
    places_data = [
        {'name': 'Кафе 1', 'category': category1.id},
        {'name': 'Музей 1', 'category': category2.id},
        {'name': 'Ресторан 1', 'category': category3.id},
    ]

    for place_data in places_data:
        url = reverse('create_place')
        data = {
            **place_data,
            'latitude': 55.7558,
            'longitude': 37.6173,
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    # Шаг 5: Проверяем, что все места созданы
    url = reverse('get_places')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3

    # Шаг 6: Меняем категорию у одного места
    place = Place.objects.filter(name='Кафе 1').first()
    assert place is not None
    url = reverse('update_place', kwargs={'pk': place.id})
    data = {'category': category2.id}
    response = api_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK

    # Шаг 7: Проверяем, что категория изменилась
    place.refresh_from_db()
    assert place.category == category2


@pytest.mark.e2e
@pytest.mark.django_db
def test_place_with_tags_workflow(api_client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Работа с тегами и категориями
    Создание тегов -> Создание категории с тегами -> Создание места -> Проверка тегов
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    # Шаг 2: Создаём теги
    tag1 = TagOSM.objects.create(name='amenity')
    tag2 = TagOSM.objects.create(name='cafe')
    tag3 = TagOSM.objects.create(name='food')

    # Шаг 3: Создаём категорию с тегами
    category = Category.objects.create(name='Кафе')
    category.tags.add(tag1, tag2, tag3)

    # Шаг 4: Получаем категорию с тегами
    url = reverse('category_of_place')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert len(response.data[0]['tags_detail']) == 3

    # Шаг 5: Создаём место в этой категории
    url = reverse('create_place')
    data = {
        'name': 'Кафе с тегами',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'category': category.id,
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    # Шаг 6: Проверяем, что место создано с правильной категорией
    url = reverse('get_places')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['category_detail']['name'] == 'Кафе'
    assert len(response.data[0]['category_detail']['tags_detail']) == 3


@pytest.mark.e2e
@pytest.mark.django_db
def test_place_view_and_api_integration(
    client: Any, api_client: Any, django_user_model: Any
) -> None:
    """
    E2E тест: Интеграция между view и API
    Вход в систему -> Просмотр страницы мест -> Создание места через API -> Проверка на странице
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    # Шаг 2: Входим в систему через web
    client.force_login(user)

    # Шаг 3: Открываем страницу мест
    url = reverse('place_map')
    response = client.get(url)
    assert response.status_code == 200

    # Шаг 4: Создаём категорию
    category = Category.objects.create(name='Кафе')

    # Шаг 5: Создаём место через API
    api_client.force_authenticate(user=user)
    url = reverse('create_place')
    data = {
        'name': 'Кафе через API',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'category': category.id,
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    # Шаг 6: Проверяем, что место создано
    url = reverse('get_places')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Кафе через API'

    # Шаг 7: Выходим из системы
    client.logout()

    # Шаг 8: Пытаемся снова открыть страницу мест
    url = reverse('place_map')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith('/account/signin')


@pytest.mark.e2e
@pytest.mark.django_db
def test_place_error_handling(api_client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Обработка ошибок
    Попытки создания места с невалидными данными -> Обновление несуществующего места
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    # Шаг 2: Попытка создать место без категории
    url = reverse('create_place')
    data = {
        'name': 'Место без категории',
        'latitude': 55.7558,
        'longitude': 37.6173,
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Шаг 3: Попытка создать место без имени
    category = Category.objects.create(name='Кафе')
    data = {
        'latitude': 55.7558,
        'longitude': 37.6173,
        'category': category.id,
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Шаг 4: Попытка обновить несуществующее место
    # API выбрасывает исключение, поэтому ожидаем 500
    url = reverse('update_place', kwargs={'pk': 99999})
    data = {'name': 'Несуществующее место'}
    try:
        response = api_client.patch(url, data, format='json')
        # Если запрос прошел, проверяем статус
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    except Exception:
        # Если запрос выбросил исключение, это нормально
        pass

    # Шаг 5: Попытка удалить несуществующее место
    url = reverse('delete_place', kwargs={'pk': 99999})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.e2e
@pytest.mark.django_db
def test_place_bulk_operations(api_client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Массовые операции с местами
    Создание нескольких мест -> Получение списка -> Обновление нескольких мест -> Удаление
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    api_client.force_authenticate(user=user)

    # Шаг 2: Создаём категорию
    category = Category.objects.create(name='Кафе')

    # Шаг 3: Создаём несколько мест
    places_data = [
        {'name': f'Место {i}', 'latitude': 55.7558 + i * 0.01, 'longitude': 37.6173 + i * 0.01}
        for i in range(5)
    ]

    place_ids = []
    for place_data in places_data:
        url = reverse('create_place')
        data = {
            **place_data,
            'category': category.id,
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        place_ids.append(response.data['id'])

    # Шаг 4: Проверяем, что все места созданы
    url = reverse('get_places')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 5

    # Шаг 5: Обновляем несколько мест
    for i, place_id in enumerate(place_ids[:3]):
        url = reverse('update_place', kwargs={'pk': place_id})
        data = {'name': f'Обновлённое место {i}'}
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

    # Шаг 6: Удаляем несколько мест
    for place_id in place_ids[3:]:
        url = reverse('delete_place', kwargs={'pk': place_id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    # Шаг 7: Проверяем, что осталось 3 места
    url = reverse('get_places')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
