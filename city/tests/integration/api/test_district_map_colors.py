"""
Тесты для API настроек цветов карты районов (get_district_map_colors, save_district_map_colors).

Покрывает:
- Аутентификацию и права доступа (GET/POST)
- GET: возврат сохранённых цветов или null при отсутствии записи
- POST: валидация формата #rrggbb, обязательность хотя бы одного цвета
- POST: сохранение и обновление (update_or_create)
- POST: частичное обновление (только один цвет)
- Изоляцию по пользователю

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

from city.models import DistrictMapColorSettings

GET_COLORS_URL = reverse('api__get_district_map_colors')
SAVE_COLORS_URL = reverse('api__save_district_map_colors')


# Fixtures


@pytest.fixture
def api_client() -> APIClient:
    """Создаёт APIClient для тестирования."""
    return APIClient()


@pytest.fixture
def authenticated_user(api_client: APIClient, django_user_model: Type[User]) -> User:
    """Создаёт аутентифицированного пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    api_client.force_authenticate(user=user)
    return user


# GET get_district_map_colors — доступ и методы


@pytest.mark.integration
def test_get_colors_guest_returns_401(api_client: APIClient) -> None:
    """Без авторизации GET возвращает 401."""
    response = api_client.get(GET_COLORS_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data


@pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
@pytest.mark.integration
def test_get_colors_prohibited_methods(
    api_client: APIClient, authenticated_user: User, method: str
) -> None:
    """Для GET-эндпоинта запрещённые методы возвращают 405."""
    client_method = getattr(api_client, method)
    response = client_method(GET_COLORS_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# GET get_district_map_colors — содержимое ответа


@pytest.mark.integration
def test_get_colors_when_no_settings_returns_nulls(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Если у пользователя нет записи, возвращаются оба null."""
    response = api_client.get(GET_COLORS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['color_visited'] is None
    assert response.data['color_not_visited'] is None


@pytest.mark.integration
def test_get_colors_returns_saved_settings(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Возвращаются сохранённые цвета пользователя."""
    DistrictMapColorSettings.objects.create(
        user=authenticated_user,
        color_visited='#4fbf4f',
        color_not_visited='#bbbbbb',
    )
    response = api_client.get(GET_COLORS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['color_visited'] == '#4fbf4f'
    assert response.data['color_not_visited'] == '#bbbbbb'


@pytest.mark.integration
def test_get_colors_returns_partial_settings(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Возвращаются частичные настройки (только один цвет задан)."""
    DistrictMapColorSettings.objects.create(
        user=authenticated_user,
        color_visited='#ff0000',
        color_not_visited=None,
    )
    response = api_client.get(GET_COLORS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['color_visited'] == '#ff0000'
    assert response.data['color_not_visited'] is None


# POST save_district_map_colors — доступ и методы


@pytest.mark.integration
def test_save_colors_guest_returns_401(api_client: APIClient) -> None:
    """Без авторизации POST возвращает 401."""
    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '#4fbf4f', 'color_not_visited': '#bbbbbb'},
        format='json',
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize('method', ['get', 'put', 'patch', 'delete'])
@pytest.mark.integration
def test_save_colors_prohibited_methods(
    api_client: APIClient, authenticated_user: User, method: str
) -> None:
    """Для POST-эндпоинта сохранения запрещённые методы возвращают 405."""
    client_method = getattr(api_client, method)
    response = client_method(SAVE_COLORS_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# POST save_district_map_colors — валидация


@pytest.mark.integration
def test_save_colors_missing_both_returns_400(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Если не передан ни color_visited, ни color_not_visited — 400."""
    response = api_client.post(SAVE_COLORS_URL, {}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'хотя бы один' in response.data['detail'].lower() or 'color' in response.data['detail'].lower()


@pytest.mark.integration
def test_save_colors_invalid_hex_visited_returns_400(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Недопустимый формат color_visited возвращает 400."""
    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': 'not-a-hex', 'color_not_visited': '#bbbbbb'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'color_visited' in response.data['detail'].lower() or 'формат' in response.data['detail'].lower()


@pytest.mark.integration
def test_save_colors_invalid_hex_not_visited_returns_400(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Недопустимый формат color_not_visited возвращает 400."""
    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '#4fbf4f', 'color_not_visited': 'xyz'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'color_not_visited' in response.data['detail'].lower() or 'формат' in response.data['detail'].lower()


@pytest.mark.integration
def test_save_colors_short_hex_returns_400(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Короткая строка вместо #rrggbb возвращает 400."""
    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '#fff', 'color_not_visited': '#bbbbbb'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.integration
def test_save_colors_no_hash_returns_400(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Строка без # возвращает 400."""
    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '4fbf4f', 'color_not_visited': '#bbbbbb'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# POST save_district_map_colors — успешное сохранение


@pytest.mark.integration
def test_save_colors_both_valid_creates_record(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Передача обоих валидных цветов создаёт запись."""
    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '#4fbf4f', 'color_not_visited': '#bbbbbb'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('status') == 'success'

    settings = DistrictMapColorSettings.objects.get(user=authenticated_user)
    assert settings.color_visited == '#4fbf4f'
    assert settings.color_not_visited == '#bbbbbb'


@pytest.mark.integration
def test_save_colors_uppercase_hex_accepted(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Принимается hex в верхнем регистре (#RRGGBB)."""
    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '#4FBF4F', 'color_not_visited': '#BBBBBB'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    settings = DistrictMapColorSettings.objects.get(user=authenticated_user)
    assert settings.color_visited == '#4FBF4F'
    assert settings.color_not_visited == '#BBBBBB'


@pytest.mark.integration
def test_save_colors_only_visited_updates_one_field(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Можно передать только color_visited — создаётся запись с одним полем."""
    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '#ff0000'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    settings = DistrictMapColorSettings.objects.get(user=authenticated_user)
    assert settings.color_visited == '#ff0000'
    assert settings.color_not_visited is None


@pytest.mark.integration
def test_save_colors_only_not_visited_updates_one_field(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Можно передать только color_not_visited."""
    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_not_visited': '#00ff00'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    settings = DistrictMapColorSettings.objects.get(user=authenticated_user)
    assert settings.color_visited is None
    assert settings.color_not_visited == '#00ff00'


@pytest.mark.integration
def test_save_colors_update_existing(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Повторный POST обновляет существующую запись (update_or_create)."""
    DistrictMapColorSettings.objects.create(
        user=authenticated_user,
        color_visited='#4fbf4f',
        color_not_visited='#bbbbbb',
    )

    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '#ff0000', 'color_not_visited': '#00ff00'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert DistrictMapColorSettings.objects.filter(user=authenticated_user).count() == 1
    settings = DistrictMapColorSettings.objects.get(user=authenticated_user)
    assert settings.color_visited == '#ff0000'
    assert settings.color_not_visited == '#00ff00'


@pytest.mark.integration
def test_save_colors_partial_update_only_visited(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Частичное обновление: передаём только color_visited — обновляется только он."""
    DistrictMapColorSettings.objects.create(
        user=authenticated_user,
        color_visited='#4fbf4f',
        color_not_visited='#bbbbbb',
    )

    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '#0000ff'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    settings = DistrictMapColorSettings.objects.get(user=authenticated_user)
    assert settings.color_visited == '#0000ff'
    assert settings.color_not_visited == '#bbbbbb'


@pytest.mark.integration
def test_save_colors_empty_string_clears_field(
    api_client: APIClient, authenticated_user: User
) -> None:
    """Пустая строка для цвета сохраняется как null (очистка поля)."""
    DistrictMapColorSettings.objects.create(
        user=authenticated_user,
        color_visited='#4fbf4f',
        color_not_visited='#bbbbbb',
    )

    response = api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '', 'color_not_visited': '#bbbbbb'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    settings = DistrictMapColorSettings.objects.get(user=authenticated_user)
    assert settings.color_visited is None or settings.color_visited == ''
    assert settings.color_not_visited == '#bbbbbb'


# Изоляция по пользователю


@pytest.mark.integration
def test_get_colors_is_user_specific(
    api_client: APIClient, django_user_model: Type[User]
) -> None:
    """GET возвращает только настройки текущего пользователя."""
    user1 = django_user_model.objects.create_user(username='user1', password='pass')
    user2 = django_user_model.objects.create_user(username='user2', password='pass')

    DistrictMapColorSettings.objects.create(
        user=user1,
        color_visited='#ff0000',
        color_not_visited='#00ff00',
    )
    DistrictMapColorSettings.objects.create(
        user=user2,
        color_visited='#0000ff',
        color_not_visited='#ffff00',
    )

    api_client.force_authenticate(user=user1)
    response = api_client.get(GET_COLORS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['color_visited'] == '#ff0000'
    assert response.data['color_not_visited'] == '#00ff00'

    api_client.force_authenticate(user=user2)
    response = api_client.get(GET_COLORS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['color_visited'] == '#0000ff'
    assert response.data['color_not_visited'] == '#ffff00'


@pytest.mark.integration
def test_save_colors_is_user_specific(
    api_client: APIClient, django_user_model: Type[User]
) -> None:
    """POST сохраняет настройки только для текущего пользователя."""
    user1 = django_user_model.objects.create_user(username='user1', password='pass')
    user2 = django_user_model.objects.create_user(username='user2', password='pass')

    api_client.force_authenticate(user=user1)
    api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '#ff0000', 'color_not_visited': '#00ff00'},
        format='json',
    )

    api_client.force_authenticate(user=user2)
    api_client.post(
        SAVE_COLORS_URL,
        {'color_visited': '#0000ff', 'color_not_visited': '#ffff00'},
        format='json',
    )

    assert DistrictMapColorSettings.objects.count() == 2
    settings1 = DistrictMapColorSettings.objects.get(user=user1)
    settings2 = DistrictMapColorSettings.objects.get(user=user2)
    assert settings1.color_visited == '#ff0000'
    assert settings2.color_visited == '#0000ff'
