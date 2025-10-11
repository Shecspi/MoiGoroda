"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, Mock

from account.models import ShareSettings


# ===== Фикстуры =====


@pytest.fixture
def create_test_user(django_user_model):
    """Создаёт тестового пользователя"""
    return django_user_model.objects.create_user(
        username='testuser', email='test@example.com', password='password123'
    )


# ===== Тесты для Statistics View =====


@pytest.mark.integration
@pytest.mark.django_db
def test_statistics_view_get_request_authenticated(client, create_test_user):
    """Тест GET запроса на страницу статистики для авторизованного пользователя"""
    client.force_login(create_test_user)

    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    assert response.status_code == 200
    assert 'account/statistics/statistics.html' in (t.name for t in response.templates)
    assert 'Личная статистика' in response.context['page_title']


@pytest.mark.integration
@pytest.mark.django_db
def test_statistics_view_get_request_unauthenticated(client):
    """Тест что неавторизованный пользователь перенаправляется"""
    response = client.get(reverse('stats'))

    assert response.status_code == 302
    assert response.url.startswith('/account/signin')


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_statistics_view_logs_access(mock_logger, client, create_test_user):
    """Тест что доступ к статистике логируется"""
    client.force_login(create_test_user)

    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            client.get(reverse('stats'))

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args[0]
    assert 'testuser' in call_args[1]
    assert 'test@example.com' in call_args[1]


@pytest.mark.integration
@pytest.mark.django_db
def test_statistics_view_no_visited_cities_shows_fake_data(client, create_test_user):
    """Тест что при отсутствии посещённых городов показываются фейковые данные"""
    client.force_login(create_test_user)

    with patch('account.views.statistics.get_number_of_visited_cities', return_value=0):
        with patch('account.views.statistics.get_fake_statistics', return_value={'fake': True}):
            response = client.get(reverse('stats'))

    assert response.status_code == 200
    assert response.context['fake_statistics'] is True
    assert 'fake' in response.context


@pytest.mark.integration
@pytest.mark.django_db
def test_statistics_view_with_visited_cities_shows_real_data(client, create_test_user):
    """Тест что при наличии посещённых городов показываются реальные данные"""
    client.force_login(create_test_user)

    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts',
            return_value={'real_data': 'value'},
        ):
            response = client.get(reverse('stats'))

    assert response.status_code == 200
    assert (
        'fake_statistics' not in response.context
        or response.context.get('fake_statistics') is not True
    )
    assert 'real_data' in response.context


@pytest.mark.integration
@pytest.mark.django_db
def test_statistics_view_share_settings_not_exist(client, create_test_user):
    """Тест контекста настроек публикации когда ShareSettings не существует"""
    client.force_login(create_test_user)

    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    assert response.status_code == 200
    assert 'share_settings' in response.context
    share_settings = response.context['share_settings']

    assert share_settings['switch_share_general'] is False
    assert share_settings['switch_share_basic_info'] is False
    assert share_settings['switch_share_city_map'] is False
    assert share_settings['switch_share_region_map'] is False
    assert share_settings['switch_subscribe'] is False


@pytest.mark.integration
@pytest.mark.django_db
def test_statistics_view_share_settings_exist_all_false(client, create_test_user):
    """Тест контекста настроек публикации когда все настройки выключены"""
    client.force_login(create_test_user)

    # Создаём ShareSettings со всеми флагами False
    ShareSettings.objects.create(
        user=create_test_user,
        can_share=False,
        can_share_dashboard=False,
        can_share_city_map=False,
        can_share_region_map=False,
        can_subscribe=False,
    )

    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    assert response.status_code == 200
    share_settings = response.context['share_settings']

    assert share_settings['switch_share_general'] is False
    assert share_settings['switch_share_basic_info'] is False
    assert share_settings['switch_share_city_map'] is False
    assert share_settings['switch_share_region_map'] is False
    assert share_settings['switch_subscribe'] is False


@pytest.mark.integration
@pytest.mark.django_db
def test_statistics_view_share_settings_exist_all_true(client, create_test_user):
    """Тест контекста настроек публикации когда все настройки включены"""
    client.force_login(create_test_user)

    # Создаём ShareSettings со всеми флагами True
    ShareSettings.objects.create(
        user=create_test_user,
        can_share=True,
        can_share_dashboard=True,
        can_share_city_map=True,
        can_share_region_map=True,
        can_subscribe=True,
    )

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


@pytest.mark.integration
@pytest.mark.django_db
def test_statistics_view_context_data(client, create_test_user):
    """Тест наличия необходимых данных в контексте"""
    client.force_login(create_test_user)

    with patch('account.views.statistics.get_number_of_visited_cities', return_value=5):
        with patch(
            'account.views.statistics.get_info_for_statistic_cards_and_charts', return_value={}
        ):
            response = client.get(reverse('stats'))

    assert response.status_code == 200
    assert 'active_page' in response.context
    assert response.context['active_page'] == 'stats'
    assert 'page_title' in response.context
    assert 'page_description' in response.context


# ===== Тесты для save_share_settings =====


@pytest.mark.integration
@pytest.mark.django_db
def test_save_share_settings_get_request_returns_404(client, create_test_user):
    """Тест что GET запрос на save_share_settings возвращает 404"""
    client.force_login(create_test_user)

    response = client.get(reverse('save_share_settings'))
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
def test_save_share_settings_unauthenticated(client):
    """Тест что неавторизованный пользователь перенаправляется"""
    response = client.post(reverse('save_share_settings'))

    assert response.status_code == 302
    assert response.url.startswith('/account/signin')


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_save_share_settings_all_enabled(mock_logger, client, create_test_user):
    """Тест сохранения настроек со всеми включёнными флагами"""
    client.force_login(create_test_user)

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

    # Проверяем, что настройки сохранены в БД
    share_settings = ShareSettings.objects.get(user=create_test_user)
    assert share_settings.can_share is True
    assert share_settings.can_share_dashboard is True
    assert share_settings.can_share_city_map is True
    assert share_settings.can_share_region_map is True
    assert share_settings.can_subscribe is True

    mock_logger.info.assert_called_once()


@pytest.mark.integration
@pytest.mark.django_db
def test_save_share_settings_all_disabled(client, create_test_user):
    """Тест сохранения настроек со всеми выключенными флагами"""
    client.force_login(create_test_user)

    # Отправляем пустой POST (все флаги False)
    response = client.post(reverse('save_share_settings'), data={})

    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

    # Проверяем, что настройки сохранены в БД
    share_settings = ShareSettings.objects.get(user=create_test_user)
    assert share_settings.can_share is False
    assert share_settings.can_share_dashboard is False
    assert share_settings.can_share_city_map is False
    assert share_settings.can_share_region_map is False
    assert share_settings.can_subscribe is False


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_save_share_settings_main_on_but_all_others_off_returns_fail(
    mock_logger, client, create_test_user
):
    """Тест что основной флаг включён, но все дополнительные выключены - возвращается ошибка"""
    client.force_login(create_test_user)

    data = {'switch_share_general': 'on'}

    response = client.post(reverse('save_share_settings'), data=data)

    assert response.status_code == 200
    assert response.json()['status'] == 'fail'
    assert 'message' in response.json()

    # Проверяем, что настройки НЕ сохранены в БД
    assert not ShareSettings.objects.filter(user=create_test_user).exists()

    mock_logger.warning.assert_called_once()


@pytest.mark.integration
@pytest.mark.django_db
@patch('account.views.statistics.logger')
def test_save_share_settings_main_off_but_others_on_corrects_to_all_off(
    mock_logger, client, create_test_user
):
    """Тест что если основной флаг выключен, то все остальные тоже выключаются"""
    client.force_login(create_test_user)

    data = {
        # switch_share_general отсутствует (False)
        'switch_share_dashboard': 'on',
        'switch_share_city_map': 'on',
        'switch_share_region_map': 'on',
        'switch_subscribe': 'on',
    }

    response = client.post(reverse('save_share_settings'), data=data)

    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

    # Проверяем, что все флаги сохранены как False
    share_settings = ShareSettings.objects.get(user=create_test_user)
    assert share_settings.can_share is False
    assert share_settings.can_share_dashboard is False
    assert share_settings.can_share_city_map is False
    assert share_settings.can_share_region_map is False
    assert share_settings.can_subscribe is False

    mock_logger.warning.assert_called_once()


@pytest.mark.integration
@pytest.mark.django_db
def test_save_share_settings_partial_flags(client, create_test_user):
    """Тест сохранения настроек с частично включёнными флагами"""
    client.force_login(create_test_user)

    data = {
        'switch_share_general': 'on',
        'switch_share_dashboard': 'on',
        'switch_share_city_map': 'on',
        # switch_share_region_map не передаётся
        # switch_subscribe не передаётся
    }

    response = client.post(reverse('save_share_settings'), data=data)

    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

    share_settings = ShareSettings.objects.get(user=create_test_user)
    assert share_settings.can_share is True
    assert share_settings.can_share_dashboard is True
    assert share_settings.can_share_city_map is True
    assert share_settings.can_share_region_map is False
    assert share_settings.can_subscribe is False


@pytest.mark.integration
@pytest.mark.django_db
def test_save_share_settings_update_existing(client, create_test_user):
    """Тест обновления существующих настроек"""
    client.force_login(create_test_user)

    # Создаём начальные настройки
    ShareSettings.objects.create(
        user=create_test_user,
        can_share=True,
        can_share_dashboard=True,
        can_share_city_map=False,
        can_share_region_map=False,
        can_subscribe=False,
    )

    # Обновляем настройки
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

    # Проверяем, что запись обновилась, а не создалась новая
    assert ShareSettings.objects.filter(user=create_test_user).count() == 1

    share_settings = ShareSettings.objects.get(user=create_test_user)
    assert share_settings.can_share is True
    assert share_settings.can_share_dashboard is True
    assert share_settings.can_share_city_map is True
    assert share_settings.can_share_region_map is True
    assert share_settings.can_subscribe is True


@pytest.mark.integration
@pytest.mark.django_db
def test_save_share_settings_creates_new_if_not_exists(client, create_test_user):
    """Тест создания новых настроек если они не существуют"""
    client.force_login(create_test_user)

    assert not ShareSettings.objects.filter(user=create_test_user).exists()

    data = {
        'switch_share_general': 'on',
        'switch_share_dashboard': 'on',
        'switch_share_city_map': 'on',
    }

    response = client.post(reverse('save_share_settings'), data=data)

    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

    assert ShareSettings.objects.filter(user=create_test_user).exists()
