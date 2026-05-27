"""Проверка записи analytics.ModeSwitchLog при переключении режима отображения."""

import json

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from rest_framework import status

from analytics.models import ModeSwitchLog


@pytest.fixture
def client() -> Client:
    return Client()


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_authenticated_user_mode_switch_creates_log(
    client: Client, django_user_model: type[User]
) -> None:
    """Авторизованный пользователь: user_id заполнен."""
    user = django_user_model.objects.create_user(username='auth_user', password='pw')
    client.force_login(user)

    response = client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': 'RU-MOW',
                'mode_from': 'markers',
                'mode_to': 'polygons',
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_201_CREATED

    row = ModeSwitchLog.objects.get(region_slug='RU-MOW')
    assert row.user == user
    assert row.region_slug == 'RU-MOW'
    assert row.mode_from == 'markers'
    assert row.mode_to == 'polygons'
    assert row.created_at is not None


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_anonymous_user_mode_switch_creates_log(client: Client) -> None:
    """Анонимный пользователь: user=None."""
    response = client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': 'RU-SPE',
                'mode_from': 'polygons',
                'mode_to': 'markers',
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_201_CREATED

    row = ModeSwitchLog.objects.get()
    assert row.user is None
    assert row.region_slug == 'RU-SPE'
    assert row.mode_from == 'polygons'
    assert row.mode_to == 'markers'


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_multiple_logs_for_same_user_and_region(
    client: Client, django_user_model: type[User]
) -> None:
    """Несколько переключений для одного пользователя в одном регионе создаются без ошибок."""
    user = django_user_model.objects.create_user(username='multi', password='pw')
    client.force_login(user)

    for mode_from, mode_to in [
        ('markers', 'polygons'),
        ('polygons', 'markers'),
        ('markers', 'polygons'),
    ]:
        response = client.post(
            reverse('api__mode_switch'),
            data=json.dumps(
                {
                    'region_slug': 'RU-MOW',
                    'mode_from': mode_from,
                    'mode_to': mode_to,
                }
            ),
            content_type='application/json',
        )
        assert response.status_code == status.HTTP_201_CREATED

    assert ModeSwitchLog.objects.filter(user=user, region_slug='RU-MOW').count() == 3  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Required fields validation
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_mode_switch_requires_region_slug(client: Client) -> None:
    """Поле region_slug обязательно."""
    response = client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'mode_from': 'markers',
                'mode_to': 'polygons',
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_mode_switch_requires_mode_from(client: Client) -> None:
    """Поле mode_from обязательно."""
    response = client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': 'RU-MOW',
                'mode_to': 'polygons',
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_mode_switch_requires_mode_to(client: Client) -> None:
    """Поле mode_to обязательно."""
    response = client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': 'RU-MOW',
                'mode_from': 'markers',
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Literal validation (mode_from / mode_to must be "markers" or "polygons")
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_invalid_mode_from_rejected(client: Client) -> None:
    """Недопустимое значение mode_from → 400."""
    response = client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': 'RU-MOW',
                'mode_from': 'invalid_mode',
                'mode_to': 'polygons',
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ModeSwitchLog.objects.count() == 0


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_invalid_mode_to_rejected(client: Client) -> None:
    """Недопустимое значение mode_to → 400."""
    response = client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': 'RU-MOW',
                'mode_from': 'markers',
                'mode_to': 'границы',
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ModeSwitchLog.objects.count() == 0


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_both_modes_invalid_rejected(client: Client) -> None:
    """Оба поля mode_from и mode_to недопустимы → 400."""
    response = client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': 'RU-MOW',
                'mode_from': 'list',
                'mode_to': 'map',
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ModeSwitchLog.objects.count() == 0


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_empty_string_mode_from_rejected(client: Client) -> None:
    """Пустая строка в mode_from → 400."""
    response = client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': 'RU-MOW',
                'mode_from': '',
                'mode_to': 'polygons',
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ModeSwitchLog.objects.count() == 0


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_empty_string_mode_to_rejected(client: Client) -> None:
    """Пустая строка в mode_to → 400."""
    response = client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': 'RU-MOW',
                'mode_from': 'markers',
                'mode_to': '',
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ModeSwitchLog.objects.count() == 0


# ---------------------------------------------------------------------------
# Malformed / empty body
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_malformed_json_rejected(client: Client) -> None:
    """Невалидный JSON → 400."""
    response = client.post(
        reverse('api__mode_switch'),
        data='not json at all',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ModeSwitchLog.objects.count() == 0


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_empty_body_rejected(client: Client) -> None:
    """Пустое тело → 400."""
    response = client.post(
        reverse('api__mode_switch'),
        data='',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ModeSwitchLog.objects.count() == 0


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_null_values_rejected(client: Client) -> None:
    """null вместо строковых значений → 400."""
    response = client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': None,
                'mode_from': None,
                'mode_to': None,
            }
        ),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ModeSwitchLog.objects.count() == 0


# ---------------------------------------------------------------------------
# HTTP method restrictions
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_get_not_allowed(client: Client) -> None:
    """GET-запрос → 405."""
    response = client.get(reverse('api__mode_switch'))
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_put_not_allowed(client: Client) -> None:
    """PUT-запрос → 405."""
    response = client.put(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': 'RU-MOW',
                'mode_from': 'markers',
                'mode_to': 'polygons',
            }
        ),
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_delete_not_allowed(client: Client) -> None:
    """DELETE-запрос → 405."""
    response = client.delete(reverse('api__mode_switch'))
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_created_at_auto_populated(client: Client, django_user_model: type[User]) -> None:
    """created_at заполняется автоматически."""
    user = django_user_model.objects.create_user(username='ts_user', password='pw')
    client.force_login(user)

    client.post(
        reverse('api__mode_switch'),
        data=json.dumps(
            {
                'region_slug': 'RU-KGD',
                'mode_from': 'markers',
                'mode_to': 'polygons',
            }
        ),
        content_type='application/json',
    )

    row = ModeSwitchLog.objects.get(region_slug='RU-KGD')
    assert row.created_at is not None


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_model_str_authenticated(django_user_model: type[User]) -> None:
    """__str__ для авторизованного пользователя."""
    user = django_user_model.objects.create_user(username='str_user', password='pw')
    log = ModeSwitchLog.objects.create(
        user=user,
        region_slug='RU-MOW',
        mode_from='markers',
        mode_to='polygons',
    )
    assert str(log) == 'str_user: markers → polygons (RU-MOW)'


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_model_str_anonymous() -> None:
    """__str__ для анонимного пользователя."""
    log = ModeSwitchLog.objects.create(
        user=None,
        region_slug='RU-SPE',
        mode_from='polygons',
        mode_to='markers',
    )
    assert str(log) == 'anonymous: polygons → markers (RU-SPE)'


# ---------------------------------------------------------------------------
# Admin tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_admin_no_add_permission() -> None:
    """Админка: добавление запрещено."""
    from analytics.admin import ModeSwitchLogAdmin

    admin = ModeSwitchLogAdmin(ModeSwitchLog, None)  # type: ignore[arg-type]
    assert admin.has_add_permission(None) is False


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_admin_no_change_permission() -> None:
    """Админка: редактирование запрещено."""
    from analytics.admin import ModeSwitchLogAdmin

    admin = ModeSwitchLogAdmin(ModeSwitchLog, None)  # type: ignore[arg-type]
    assert admin.has_change_permission(None) is False


# ---------------------------------------------------------------------------
# Index tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_indexes_exist() -> None:
    """Все ожидаемые индексы присутствуют в модели."""
    index_fields = {tuple(idx.fields) for idx in ModeSwitchLog._meta.indexes}

    expected = {
        ('region_slug', 'created_at'),
        ('user', 'created_at'),
        ('mode_to', 'mode_from', 'created_at'),
    }
    assert expected == index_fields
