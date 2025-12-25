"""
Тесты для API сохранения и удаления настроек по умолчанию фильтрации и сортировки.

Покрывает:
- Аутентификацию и права доступа
- HTTP методы (POST и DELETE)
- Валидацию входных данных
- Сохранение настроек фильтрации
- Сохранение настроек сортировки
- Удаление настроек
- Обновление существующих настроек
- Логирование

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Type

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from city.models import CityListDefaultSettings

SAVE_SETTINGS_URL = reverse('api__save_city_list_default_settings')
DELETE_SETTINGS_URL = reverse('api__delete_city_list_default_settings')


# Fixtures


@pytest.fixture
def api_client() -> APIClient:
    """Создает APIClient для тестирования."""
    return APIClient()


@pytest.fixture
def authenticated_user(api_client: APIClient, django_user_model: Type[User]) -> User:
    """Создает аутентифицированного пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    api_client.force_authenticate(user=user)
    return user


# Тесты доступа и методов


@pytest.mark.integration
def test_save_settings_guest_cannot_access(api_client: APIClient) -> None:
    """Проверяет, что гость не может получить доступ к API."""
    response = api_client.post(
        SAVE_SETTINGS_URL, {'parameter_type': 'filter', 'parameter_value': 'no_filter'}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_delete_settings_guest_cannot_access(api_client: APIClient) -> None:
    """Проверяет, что гость не может получить доступ к API удаления."""
    response = api_client.delete(DELETE_SETTINGS_URL, {'parameter_type': 'filter'}, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize('method', ['get', 'put', 'patch'])
@pytest.mark.integration
def test_save_settings_prohibited_methods(
    api_client: APIClient, authenticated_user: User, method: str
) -> None:
    """Проверяет, что запрещенные методы возвращают 405."""
    client_method = getattr(api_client, method)
    response = client_method(SAVE_SETTINGS_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.parametrize('method', ['get', 'post', 'put', 'patch'])
@pytest.mark.integration
def test_delete_settings_prohibited_methods(
    api_client: APIClient, authenticated_user: User, method: str
) -> None:
    """Проверяет, что запрещенные методы возвращают 405."""
    client_method = getattr(api_client, method)
    response = client_method(DELETE_SETTINGS_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# Тесты валидации


@pytest.mark.integration
def test_save_settings_missing_parameter_type(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет валидацию при отсутствии parameter_type."""
    response = api_client.post(SAVE_SETTINGS_URL, {'parameter_value': 'no_filter'}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'parameter_type' in response.data['detail'].lower()


@pytest.mark.integration
def test_save_settings_missing_parameter_value(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет валидацию при отсутствии parameter_value."""
    response = api_client.post(SAVE_SETTINGS_URL, {'parameter_type': 'filter'}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'parameter_value' in response.data['detail'].lower()


@pytest.mark.integration
def test_save_settings_invalid_parameter_type(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет валидацию при недопустимом parameter_type."""
    response = api_client.post(
        SAVE_SETTINGS_URL,
        {'parameter_type': 'invalid', 'parameter_value': 'no_filter'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'parameter_type' in response.data['detail'].lower()


@pytest.mark.integration
def test_save_settings_invalid_filter_value(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет валидацию при недопустимом значении фильтра."""
    response = api_client.post(
        SAVE_SETTINGS_URL,
        {'parameter_type': 'filter', 'parameter_value': 'invalid_filter'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'фильтра' in response.data['detail'].lower()


@pytest.mark.integration
def test_save_settings_invalid_sort_value(api_client: APIClient, authenticated_user: User) -> None:
    """Проверяет валидацию при недопустимом значении сортировки."""
    response = api_client.post(
        SAVE_SETTINGS_URL,
        {'parameter_type': 'sort', 'parameter_value': 'invalid_sort'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'сортировки' in response.data['detail'].lower()


@pytest.mark.integration
def test_delete_settings_missing_parameter_type(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет валидацию при отсутствии parameter_type при удалении."""
    response = api_client.delete(DELETE_SETTINGS_URL, {}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'parameter_type' in response.data['detail'].lower()


@pytest.mark.integration
def test_delete_settings_invalid_parameter_type(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет валидацию при недопустимом parameter_type при удалении."""
    response = api_client.delete(DELETE_SETTINGS_URL, {'parameter_type': 'invalid'}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'parameter_type' in response.data['detail'].lower()


# Тесты сохранения настроек фильтрации


@pytest.mark.parametrize(
    'filter_value', ['no_filter', 'no_magnet', 'magnet', 'current_year', 'last_year']
)
@pytest.mark.integration
def test_save_filter_settings_valid_values(
    api_client: APIClient, authenticated_user: User, filter_value: str
) -> None:
    """Проверяет сохранение различных значений фильтрации."""
    response = api_client.post(
        SAVE_SETTINGS_URL,
        {'parameter_type': 'filter', 'parameter_value': filter_value},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'success'
    assert CityListDefaultSettings.objects.filter(
        user=authenticated_user, parameter_type='filter', parameter_value=filter_value
    ).exists()


@pytest.mark.integration
def test_save_filter_settings_update_existing(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет обновление существующей настройки фильтрации."""
    # Создаём начальную настройку
    CityListDefaultSettings.objects.create(
        user=authenticated_user, parameter_type='filter', parameter_value='no_filter'
    )

    # Обновляем значение
    response = api_client.post(
        SAVE_SETTINGS_URL,
        {'parameter_type': 'filter', 'parameter_value': 'magnet'},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'success'
    assert not CityListDefaultSettings.objects.filter(
        user=authenticated_user, parameter_type='filter', parameter_value='no_filter'
    ).exists()
    assert CityListDefaultSettings.objects.filter(
        user=authenticated_user, parameter_type='filter', parameter_value='magnet'
    ).exists()


# Тесты сохранения настроек сортировки


@pytest.mark.parametrize(
    'sort_value',
    [
        'name_down',
        'name_up',
        'first_visit_date_down',
        'first_visit_date_up',
        'last_visit_date_down',
        'last_visit_date_up',
        'number_of_visits_down',
        'number_of_visits_up',
        'date_of_foundation_down',
        'date_of_foundation_up',
        'number_of_users_who_visit_city_down',
        'number_of_users_who_visit_city_up',
        'number_of_visits_all_users_down',
        'number_of_visits_all_users_up',
    ],
)
@pytest.mark.integration
def test_save_sort_settings_valid_values(
    api_client: APIClient, authenticated_user: User, sort_value: str
) -> None:
    """Проверяет сохранение различных значений сортировки."""
    response = api_client.post(
        SAVE_SETTINGS_URL,
        {'parameter_type': 'sort', 'parameter_value': sort_value},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'success'
    assert CityListDefaultSettings.objects.filter(
        user=authenticated_user, parameter_type='sort', parameter_value=sort_value
    ).exists()


@pytest.mark.integration
def test_save_sort_settings_update_existing(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет обновление существующей настройки сортировки."""
    # Создаём начальную настройку
    CityListDefaultSettings.objects.create(
        user=authenticated_user, parameter_type='sort', parameter_value='name_down'
    )

    # Обновляем значение
    response = api_client.post(
        SAVE_SETTINGS_URL,
        {'parameter_type': 'sort', 'parameter_value': 'last_visit_date_up'},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'success'
    assert not CityListDefaultSettings.objects.filter(
        user=authenticated_user, parameter_type='sort', parameter_value='name_down'
    ).exists()
    assert CityListDefaultSettings.objects.filter(
        user=authenticated_user, parameter_type='sort', parameter_value='last_visit_date_up'
    ).exists()


# Тесты удаления настроек


@pytest.mark.integration
def test_delete_filter_settings_existing(api_client: APIClient, authenticated_user: User) -> None:
    """Проверяет удаление существующей настройки фильтрации."""
    CityListDefaultSettings.objects.create(
        user=authenticated_user, parameter_type='filter', parameter_value='no_filter'
    )

    response = api_client.delete(DELETE_SETTINGS_URL, {'parameter_type': 'filter'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'success'
    assert not CityListDefaultSettings.objects.filter(
        user=authenticated_user, parameter_type='filter'
    ).exists()


@pytest.mark.integration
def test_delete_sort_settings_existing(api_client: APIClient, authenticated_user: User) -> None:
    """Проверяет удаление существующей настройки сортировки."""
    CityListDefaultSettings.objects.create(
        user=authenticated_user, parameter_type='sort', parameter_value='name_down'
    )

    response = api_client.delete(DELETE_SETTINGS_URL, {'parameter_type': 'sort'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'success'
    assert not CityListDefaultSettings.objects.filter(
        user=authenticated_user, parameter_type='sort'
    ).exists()


@pytest.mark.integration
def test_delete_settings_nonexistent(api_client: APIClient, authenticated_user: User) -> None:
    """Проверяет удаление несуществующей настройки."""
    response = api_client.delete(DELETE_SETTINGS_URL, {'parameter_type': 'filter'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'success'
    assert 'не найдены' in response.data['message'].lower()


@pytest.mark.integration
def test_delete_settings_does_not_affect_other_type(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет, что удаление одного типа не влияет на другой."""
    CityListDefaultSettings.objects.create(
        user=authenticated_user, parameter_type='filter', parameter_value='no_filter'
    )
    CityListDefaultSettings.objects.create(
        user=authenticated_user, parameter_type='sort', parameter_value='name_down'
    )

    response = api_client.delete(DELETE_SETTINGS_URL, {'parameter_type': 'filter'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert CityListDefaultSettings.objects.filter(
        user=authenticated_user, parameter_type='sort'
    ).exists()
    assert not CityListDefaultSettings.objects.filter(
        user=authenticated_user, parameter_type='filter'
    ).exists()


# Тесты изоляции пользователей


@pytest.mark.integration
def test_settings_are_user_specific(api_client: APIClient, django_user_model: Type[User]) -> None:
    """Проверяет, что настройки изолированы для каждого пользователя."""
    user1 = django_user_model.objects.create_user(username='user1', password='pass')
    user2 = django_user_model.objects.create_user(username='user2', password='pass')

    api_client.force_authenticate(user=user1)
    response1 = api_client.post(
        SAVE_SETTINGS_URL,
        {'parameter_type': 'filter', 'parameter_value': 'no_filter'},
        format='json',
    )
    assert response1.status_code == status.HTTP_200_OK

    api_client.force_authenticate(user=user2)
    response2 = api_client.post(
        SAVE_SETTINGS_URL,
        {'parameter_type': 'filter', 'parameter_value': 'magnet'},
        format='json',
    )
    assert response2.status_code == status.HTTP_200_OK

    assert CityListDefaultSettings.objects.filter(user=user1, parameter_value='no_filter').exists()
    assert CityListDefaultSettings.objects.filter(user=user2, parameter_value='magnet').exists()
    assert CityListDefaultSettings.objects.count() == 2
