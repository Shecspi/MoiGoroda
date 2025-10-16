"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from django.urls import reverse
from unittest.mock import patch

from account.models import ShareSettings


# ===== E2E тесты для настроек публикации =====


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_enable_all_share_settings_flow(
    mock_logger: Any, client: Any, django_user_model: Any
) -> None:
    """
    E2E тест: Включение всех настроек публикации -> Проверка -> Скачивание отчёта
    """
    # Шаг 1: Регистрируем пользователя
    with patch('account.views.access.logger_email'):
        signup_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'personal_data_consent': True,
            'personal_data_version': '1.0',
        }
        client.post(reverse('signup'), data=signup_data, follow=True)

    user = django_user_model.objects.get(username='testuser')

    # Шаг 2: Открываем статистику
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    # Проверяем начальное состояние настроек (все выключены)
    share_settings = response.context['share_settings']
    assert share_settings['switch_share_general'] is False

    # Шаг 3: Включаем все настройки
    data = {
        'switch_share_general': 'on',
        'switch_share_dashboard': 'on',
        'switch_share_city_map': 'on',
        'switch_share_region_map': 'on',
        'switch_subscribe': 'on',
    }
    response = client.post(reverse('save_share_settings'), data=data)

    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

    # Шаг 4: Проверяем, что настройки сохранились в БД
    db_settings = ShareSettings.objects.get(user=user)
    assert db_settings.can_share is True
    assert db_settings.can_share_dashboard is True
    assert db_settings.can_share_city_map is True
    assert db_settings.can_share_region_map is True
    assert db_settings.can_subscribe is True

    # Шаг 5: Обновляем страницу статистики
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    # Проверяем, что настройки отображаются как включённые
    share_settings = response.context['share_settings']
    assert share_settings['switch_share_general'] is True
    assert share_settings['switch_share_basic_info'] is True
    assert share_settings['switch_share_city_map'] is True
    assert share_settings['switch_share_region_map'] is True
    assert share_settings['switch_subscribe'] is True


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_partial_share_settings_flow(mock_logger: Any, client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Включение части настроек публикации
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Включаем только некоторые настройки
    data = {
        'switch_share_general': 'on',
        'switch_share_dashboard': 'on',
        'switch_share_city_map': 'on',
        # switch_share_region_map и switch_subscribe НЕ включены
    }
    response = client.post(reverse('save_share_settings'), data=data)

    assert response.json()['status'] == 'ok'

    # Шаг 3: Проверяем БД
    db_settings = ShareSettings.objects.get(user=user)
    assert db_settings.can_share is True
    assert db_settings.can_share_dashboard is True
    assert db_settings.can_share_city_map is True
    assert db_settings.can_share_region_map is False
    assert db_settings.can_subscribe is False

    # Шаг 4: Проверяем на странице
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    share_settings = response.context['share_settings']
    assert share_settings['switch_share_general'] is True
    assert share_settings['switch_share_basic_info'] is True
    assert share_settings['switch_share_city_map'] is True
    assert share_settings['switch_share_region_map'] is False
    assert share_settings['switch_subscribe'] is False


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_enable_then_disable_share_settings_flow(
    mock_logger: Any, client: Any, django_user_model: Any
) -> None:
    """
    E2E тест: Включение настроек -> Выключение -> Проверка
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Включаем настройки
    data = {
        'switch_share_general': 'on',
        'switch_share_dashboard': 'on',
        'switch_share_city_map': 'on',
    }
    client.post(reverse('save_share_settings'), data=data)

    # Проверяем, что включено
    db_settings = ShareSettings.objects.get(user=user)
    assert db_settings.can_share is True

    # Шаг 3: Выключаем всё
    response = client.post(reverse('save_share_settings'), data={})

    assert response.json()['status'] == 'ok'

    # Шаг 4: Проверяем БД
    db_settings.refresh_from_db()
    assert db_settings.can_share is False
    assert db_settings.can_share_dashboard is False  # type: ignore[unreachable]
    assert db_settings.can_share_city_map is False


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_invalid_settings_then_correct_flow(
    mock_logger: Any, client: Any, django_user_model: Any
) -> None:
    """
    E2E тест: Попытка некорректной настройки -> Ошибка -> Исправление -> Успех
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Пытаемся включить только основной флаг без дополнительных
    data = {'switch_share_general': 'on'}
    response = client.post(reverse('save_share_settings'), data=data)

    # Проверяем ошибку
    assert response.status_code == 200
    assert response.json()['status'] == 'fail'

    # Проверяем, что настройки НЕ сохранились
    assert not ShareSettings.objects.filter(user=user).exists()

    # Шаг 3: Исправляем и включаем хотя бы один дополнительный флаг
    data = {'switch_share_general': 'on', 'switch_share_dashboard': 'on'}
    response = client.post(reverse('save_share_settings'), data=data)

    assert response.json()['status'] == 'ok'

    # Проверяем, что настройки сохранились
    assert ShareSettings.objects.filter(user=user).exists()
    db_settings = ShareSettings.objects.get(user=user)
    assert db_settings.can_share is True
    assert db_settings.can_share_dashboard is True


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_update_existing_share_settings_flow(
    mock_logger: Any, client: Any, django_user_model: Any
) -> None:
    """
    E2E тест: Создание настроек -> Обновление -> Проверка что запись одна
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Создаём начальные настройки
    data = {'switch_share_general': 'on', 'switch_share_dashboard': 'on'}
    client.post(reverse('save_share_settings'), data=data)

    # Проверяем количество записей
    assert ShareSettings.objects.filter(user=user).count() == 1

    # Шаг 3: Обновляем настройки
    data = {
        'switch_share_general': 'on',
        'switch_share_dashboard': 'on',
        'switch_share_city_map': 'on',
        'switch_share_region_map': 'on',
    }
    client.post(reverse('save_share_settings'), data=data)

    # Шаг 4: Проверяем, что всё ещё одна запись (обновление, не создание)
    assert ShareSettings.objects.filter(user=user).count() == 1

    # Проверяем обновлённые значения
    db_settings = ShareSettings.objects.get(user=user)
    assert db_settings.can_share_city_map is True
    assert db_settings.can_share_region_map is True


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_share_settings_persist_after_logout_and_login(
    mock_logger: Any, client: Any, django_user_model: Any
) -> None:
    """
    E2E тест: Настройка публикации -> Выход -> Вход -> Проверка сохранения
    """
    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Настраиваем публикацию
    data = {
        'switch_share_general': 'on',
        'switch_share_dashboard': 'on',
        'switch_share_city_map': 'on',
    }
    client.post(reverse('save_share_settings'), data=data)

    # Шаг 3: Выходим
    client.post(reverse('logout'))

    # Шаг 4: Входим снова
    client.post(reverse('signin'), data={'username': 'testuser', 'password': 'password123'})

    # Шаг 5: Проверяем, что настройки сохранились
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    share_settings = response.context['share_settings']
    assert share_settings['switch_share_general'] is True
    assert share_settings['switch_share_basic_info'] is True
    assert share_settings['switch_share_city_map'] is True


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_multiple_users_independent_share_settings(
    mock_logger: Any, client: Any, django_user_model: Any
) -> None:
    """
    E2E тест: Настройки публикации независимы для разных пользователей
    """
    # Шаг 1: Создаём двух пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    # Шаг 2: Настраиваем публикацию для user1
    client.force_login(user1)
    data = {'switch_share_general': 'on', 'switch_share_dashboard': 'on'}
    client.post(reverse('save_share_settings'), data=data)

    # Шаг 3: Проверяем настройки user1
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    assert response.context['share_settings']['switch_share_general'] is True

    # Шаг 4: Логинимся как user2
    client.force_login(user2)

    # Шаг 5: Проверяем, что у user2 настройки по умолчанию (выключены)
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    assert response.context['share_settings']['switch_share_general'] is False

    # Шаг 6: Настраиваем публикацию для user2 по-другому
    data = {
        'switch_share_general': 'on',
        'switch_share_city_map': 'on',
        'switch_share_region_map': 'on',
    }
    client.post(reverse('save_share_settings'), data=data)

    # Шаг 7: Проверяем, что настройки user1 не изменились
    db_settings_user1 = ShareSettings.objects.get(user=user1)
    assert db_settings_user1.can_share_dashboard is True
    assert db_settings_user1.can_share_city_map is False

    # Проверяем настройки user2
    db_settings_user2 = ShareSettings.objects.get(user=user2)
    assert db_settings_user2.can_share_dashboard is False
    assert db_settings_user2.can_share_city_map is True


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_share_settings_with_subscription_integration(
    mock_logger: Any, client: Any, django_user_model: Any
) -> None:
    """
    E2E тест: Настройки публикации влияют на отображение в подписках
    """
    # Шаг 1: Создаём двух пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    # Шаг 2: user2 подписывается на user1
    from subscribe.infrastructure.models import Subscribe

    Subscribe.objects.create(subscribe_from=user2, subscribe_to=user1)

    # Шаг 3: Проверяем профиль user1 (can_subscribe должен быть False)
    client.force_login(user1)
    response = client.get(reverse('profile'))

    subscriber = response.context['subscriber_users'][0]
    assert subscriber.username == 'user2'
    assert subscriber.can_subscribe is False

    # Шаг 4: user2 включает публикацию статистики
    client.force_login(user2)
    data = {'switch_share_general': 'on', 'switch_share_dashboard': 'on'}
    client.post(reverse('save_share_settings'), data=data)

    # Шаг 5: Проверяем профиль user1 снова (can_subscribe должен быть True)
    client.force_login(user1)
    response = client.get(reverse('profile'))

    subscriber = response.context['subscriber_users'][0]
    assert subscriber.can_subscribe is True

    # Шаг 6: user2 выключает публикацию
    client.force_login(user2)
    client.post(reverse('save_share_settings'), data={})

    # Шаг 7: Проверяем профиль user1 (can_subscribe должен вернуться в False)
    client.force_login(user1)
    response = client.get(reverse('profile'))

    subscriber = response.context['subscriber_users'][0]
    assert subscriber.can_subscribe is False


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_complete_share_settings_journey(mock_logger: Any, client: Any) -> None:
    """
    E2E тест: Полный путь пользователя с настройками публикации
    Регистрация -> Просмотр статистики -> Включение настроек -> Изменение -> Выключение
    """
    # Шаг 1: Регистрация
    with patch('account.views.access.logger_email'):
        signup_data = {
            'username': 'journeyuser',
            'email': 'journey@example.com',
            'password1': 'JourneyPass123!',
            'password2': 'JourneyPass123!',
            'personal_data_consent': True,
            'personal_data_version': '1.0',
        }
        client.post(reverse('signup'), data=signup_data, follow=True)

    # Шаг 2: Просмотр статистики (по умолчанию всё выключено)
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    assert response.context['share_settings']['switch_share_general'] is False

    # Шаг 3: Включаем все настройки
    data = {
        'switch_share_general': 'on',
        'switch_share_dashboard': 'on',
        'switch_share_city_map': 'on',
        'switch_share_region_map': 'on',
        'switch_subscribe': 'on',
    }
    client.post(reverse('save_share_settings'), data=data)

    # Шаг 4: Проверяем, что всё включено
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    share_settings = response.context['share_settings']
    assert all(share_settings.values())

    # Шаг 5: Изменяем настройки (выключаем некоторые)
    data = {'switch_share_general': 'on', 'switch_share_dashboard': 'on'}
    client.post(reverse('save_share_settings'), data=data)

    # Шаг 6: Проверяем изменения
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    share_settings = response.context['share_settings']
    assert share_settings['switch_share_general'] is True
    assert share_settings['switch_share_basic_info'] is True
    assert share_settings['switch_share_city_map'] is False
    assert share_settings['switch_share_region_map'] is False

    # Шаг 7: Выключаем всё
    client.post(reverse('save_share_settings'), data={})

    # Шаг 8: Проверяем, что всё выключено
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    share_settings = response.context['share_settings']
    assert all(not value for value in share_settings.values())
