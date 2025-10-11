"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import json
import pytest
from django.urls import reverse
from unittest.mock import patch, Mock

from account.models import ShareSettings


# ===== E2E тесты для статистики и скачивания =====


@pytest.mark.e2e
@pytest.mark.django_db
def test_view_statistics_and_download_report_flow(client, django_user_model):
    """
    E2E тест: Вход -> Просмотр статистики -> Скачивание отчёта в разных форматах
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Открываем страницу статистики
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts',
            return_value={'cities_count': 5},
        ):
            response = client.get(reverse('stats'))

    assert response.status_code == 200
    assert 'account/statistics/statistics.html' in (t.name for t in response.templates)
    assert 'cities_count' in response.context

    # Шаг 3: Скачиваем отчёт в формате TXT
    with patch('account.views.download.CityReport') as mock_report:
        mock_report.return_value.get_report.return_value = [('Город',), ('Москва',)]
        with patch('account.views.download.logger'):
            response = client.post(
                reverse('download'), data={'reporttype': 'city', 'filetype': 'txt'}
            )

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/txt'
    assert '.txt' in response['Content-Disposition']

    # Шаг 4: Скачиваем отчёт в формате CSV
    with patch('account.views.download.CityReport') as mock_report:
        mock_report.return_value.get_report.return_value = [('Город',), ('Москва',)]
        with patch('account.views.download.logger'):
            response = client.post(
                reverse('download'), data={'reporttype': 'city', 'filetype': 'csv'}
            )

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv'

    # Шаг 5: Скачиваем отчёт в формате JSON
    with patch('account.views.download.CityReport') as mock_report:
        mock_report.return_value.get_report.return_value = [('Город',), ('Москва',)]
        with patch('account.views.download.logger'):
            response = client.post(
                reverse('download'), data={'reporttype': 'city', 'filetype': 'json'}
            )

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'


@pytest.mark.e2e
@pytest.mark.django_db
def test_statistics_shows_fake_data_then_real_data_after_visit(client, django_user_model):
    """
    E2E тест: Статистика без посещений показывает фейковые данные -> После добавления посещения показывает реальные данные
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Открываем статистику без посещений
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=0):
        with patch('account.views.statistics.get_fake_statistics', return_value={'fake': True}):
            response = client.get(reverse('stats'))

    assert response.status_code == 200
    assert response.context.get('fake_statistics') is True

    # Шаг 3: Симулируем добавление посещения и открываем статистику снова
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=1):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts',
            return_value={'cities_count': 1},
        ):
            response = client.get(reverse('stats'))

    assert response.status_code == 200
    assert response.context.get('fake_statistics') is not True
    assert 'cities_count' in response.context


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_configure_share_settings_and_verify_flow(mock_logger, client, django_user_model):
    """
    E2E тест: Настройка параметров публикации статистики -> Проверка сохранения -> Повторный просмотр
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Открываем статистику и проверяем начальные настройки
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    assert response.status_code == 200
    share_settings = response.context['share_settings']
    assert share_settings['switch_share_general'] is False

    # Шаг 3: Включаем настройки публикации
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

    # Шаг 4: Открываем статистику снова и проверяем, что настройки сохранились
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    assert response.status_code == 200
    share_settings = response.context['share_settings']
    assert share_settings['switch_share_general'] is True
    assert share_settings['switch_share_basic_info'] is True
    assert share_settings['switch_share_city_map'] is True
    assert share_settings['switch_share_region_map'] is True
    assert share_settings['switch_subscribe'] is True

    # Шаг 5: Выключаем настройки публикации
    response = client.post(reverse('save_share_settings'), data={})
    assert response.json()['status'] == 'ok'

    # Шаг 6: Проверяем, что настройки выключились
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    share_settings = response.context['share_settings']
    assert share_settings['switch_share_general'] is False


@pytest.mark.e2e
@pytest.mark.django_db
def test_download_multiple_report_types_flow(client, django_user_model):
    """
    E2E тест: Скачивание отчётов разных типов подряд
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Скачиваем отчёт о городах без группировки
    with patch('account.views.download.CityReport') as mock_report:
        mock_report.return_value.get_report.return_value = [
            ('Город', 'Дата'),
            ('Москва', '2024-01-01'),
        ]
        with patch('account.views.download.logger'):
            response = client.post(
                reverse('download'),
                data={'reporttype': 'city', 'filetype': 'txt'},
                # Не передаём group_city, чтобы использовалось значение по умолчанию (False)
            )

    assert response.status_code == 200
    # Проверяем, что CityReport был вызван (параметр group_city станет False по умолчанию)
    assert mock_report.call_count == 1

    # Шаг 3: Скачиваем отчёт о городах с группировкой
    with patch('account.views.download.CityReport') as mock_report:
        mock_report.return_value.get_report.return_value = [
            ('Город', 'Количество посещений'),
            ('Москва', '5'),
        ]
        with patch('account.views.download.logger'):
            response = client.post(
                reverse('download'),
                data={'reporttype': 'city', 'filetype': 'csv', 'group_city': 'on'},
            )

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv'

    # Шаг 4: Скачиваем в формате Excel
    with patch('account.views.download.CityReport') as mock_report:
        mock_report.return_value.get_report.return_value = [('Город',), ('Москва',)]
        with patch('account.views.download.logger'):
            response = client.post(
                reverse('download'), data={'reporttype': 'city', 'filetype': 'xls'}
            )

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/vnd.ms-excel'


@pytest.mark.e2e
@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_statistics_or_download(client):
    """
    E2E тест: Неавторизованный пользователь не может просмотреть статистику или скачать отчёт
    """
    # Шаг 1: Пытаемся просмотреть статистику без авторизации
    response = client.get(reverse('stats'))
    assert response.status_code == 302
    assert response.url.startswith('/account/signin')

    # Шаг 2: Пытаемся скачать отчёт без авторизации
    response = client.post(reverse('download'), data={'reporttype': 'city', 'filetype': 'txt'})
    assert response.status_code == 302
    assert response.url.startswith('/account/signin')


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_share_settings_validation_flow(mock_logger, client, django_user_model):
    """
    E2E тест: Проверка валидации настроек публикации (нельзя включить основной без дополнительных)
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Пытаемся включить только основной флаг без дополнительных
    data = {'switch_share_general': 'on'}
    response = client.post(reverse('save_share_settings'), data=data)

    # Проверяем, что получили ошибку
    assert response.status_code == 200
    assert response.json()['status'] == 'fail'

    # Проверяем, что настройки не сохранились
    assert not ShareSettings.objects.filter(user=user).exists()

    # Шаг 3: Исправляем и включаем хотя бы один дополнительный флаг
    data = {'switch_share_general': 'on', 'switch_share_dashboard': 'on'}
    response = client.post(reverse('save_share_settings'), data=data)

    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

    # Проверяем, что настройки сохранились
    assert ShareSettings.objects.filter(user=user).exists()


@pytest.mark.e2e
@pytest.mark.django_db
def test_statistics_page_persists_through_multiple_visits(client, django_user_model):
    """
    E2E тест: Многократный доступ к статистике сохраняет настройки
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Настраиваем публикацию
    with patch('account.views.statistics.logger'):
        data = {
            'switch_share_general': 'on',
            'switch_share_dashboard': 'on',
            'switch_share_city_map': 'on',
        }
        client.post(reverse('save_share_settings'), data=data)

    # Шаг 3: Открываем статистику несколько раз
    for _ in range(3):
        with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
            with patch(
                'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
            ):
                response = client.get(reverse('stats'))

                assert response.status_code == 200
                share_settings = response.context['share_settings']
                assert share_settings['switch_share_general'] is True
                assert share_settings['switch_share_basic_info'] is True
                assert share_settings['switch_share_city_map'] is True


@pytest.mark.e2e
@pytest.mark.django_db
def test_download_after_logout_redirects_to_signin(client, django_user_model):
    """
    E2E тест: После выхода попытка скачивания перенаправляет на вход
    """
    # Шаг 1: Создаём и логиним пользователя
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    # Шаг 2: Успешно скачиваем отчёт
    with patch('account.views.download.CityReport') as mock_report:
        mock_report.return_value.get_report.return_value = [('Город',), ('Москва',)]
        with patch('account.views.download.logger'):
            response = client.post(
                reverse('download'), data={'reporttype': 'city', 'filetype': 'txt'}
            )
    assert response.status_code == 200

    # Шаг 3: Выходим
    client.post(reverse('logout'))

    # Шаг 4: Пытаемся скачать отчёт после выхода
    response = client.post(reverse('download'), data={'reporttype': 'city', 'filetype': 'txt'})

    assert response.status_code == 302
    assert response.url.startswith('/account/signin')


@pytest.mark.e2e
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_full_statistics_workflow(mock_logger, client, django_user_model):
    """
    E2E тест: Полный рабочий процесс со статистикой
    Вход -> Просмотр фейковой статистики -> Настройка публикации -> Скачивание отчётов
    """
    # Шаг 1: Регистрация
    with patch('account.views.access.logger_email'):
        signup_data = {
            'username': 'statsuser',
            'email': 'stats@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'personal_data_consent': True,
            'personal_data_version': '1.0',
        }
        client.post(reverse('signup'), data=signup_data, follow=True)

    # Шаг 2: Просмотр фейковой статистики (нет посещений)
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=0):
        with patch('account.views.statistics.get_fake_statistics', return_value={'fake': True}):
            response = client.get(reverse('stats'))
    assert response.context.get('fake_statistics') is True

    # Шаг 3: Настройка публикации
    data = {
        'switch_share_general': 'on',
        'switch_share_dashboard': 'on',
        'switch_share_city_map': 'on',
    }
    response = client.post(reverse('save_share_settings'), data=data)
    assert response.json()['status'] == 'ok'

    # Шаг 4: Проверяем настройки (имитируем, что теперь есть посещённые города)
    with patch('account.views.statistics.get_number_of_visited_cities', return_value=1):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    share_settings = response.context['share_settings']
    assert share_settings['switch_share_general'] is True

    # Шаг 5: Скачиваем отчёты в разных форматах
    formats = ['txt', 'csv', 'json', 'xls']
    for fmt in formats:
        with patch('account.views.download.CityReport') as mock_report:
            mock_report.return_value.get_report.return_value = [('Город',), ('Москва',)]
            with patch('account.views.download.logger'):
                response = client.post(
                    reverse('download'), data={'reporttype': 'city', 'filetype': fmt}
                )
        assert response.status_code == 200
