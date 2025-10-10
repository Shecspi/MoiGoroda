"""
ИНТЕГРАЦИОННЫЕ тесты формы создания города (с реальной БД).

Эти тесты используют реальную базу данных и проверяют полный цикл работы.
⚠️ МЕДЛЕННЫЕ ТЕСТЫ (16 тестов ~5-7 секунд)

Для быстрой разработки используйте: test_city_create_form_fast.py

Покрывает:
- POST запросы для создания города
- Валидацию формы
- Обработку валидных и невалидных данных
- Автоматическое добавление пользователя
- Редиректы после успешного создания
- Проверку уникальности записей

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import date
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from unittest.mock import MagicMock, patch

from city.models import VisitedCity, City
from country.models import Country, PartOfTheWorld, Location
from region.models import Region, RegionType, Area

# Помечаем весь модуль для использования БД
pytestmark = pytest.mark.django_db


# Фикстуры


@pytest.fixture(scope='function')
def setup_db(django_user_model: Any) -> dict[str, Any]:
    """Фикстура для создания всех необходимых тестовых данных.

    Оптимизировано для скорости: создает минимальный набор объектов.
    """
    # Создаем пользователя
    user = django_user_model.objects.create_user(username='testuser', password='testpass')

    # Создаем минимальные зависимости
    part_of_world = PartOfTheWorld.objects.create(name='Test')
    location = Location.objects.create(name='Test', part_of_the_world=part_of_world)
    country = Country.objects.create(name='Test', code='T', fullname='Test', location=location)
    region_type = RegionType.objects.create(title='Обл')
    area = Area.objects.create(country=country, title='Test')
    region = Region.objects.create(
        title='Test', country=country, type=region_type, area=area, iso3166='T-T', full_name='Test'
    )
    city = City.objects.create(
        title='Test',
        country=country,
        region=region,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )

    return {'user': user, 'country': country, 'region': region, 'city': city}


# Тесты POST запросов - успешное создание


# pytestmark уже установлен для всего модуля
@patch('city.signals.notify_subscribers_on_city_add')
@patch('city.services.db.set_is_visit_first_for_all_visited_cities')
def test_city_create_with_valid_data(
    mock_set_first_visit: MagicMock,
    mock_signal: MagicMock,
    setup_db: dict[str, Any],
    client: Client,
) -> None:
    """Проверяет успешное создание посещенного города с валидными данными."""
    client.login(username='testuser', password='testpass')

    form_data = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': setup_db['city'].id,
        'date_of_visit': '15.01.2024',
        'rating': '5',
        'has_magnet': True,
        'impression': 'Great city!',
    }

    response = client.post(reverse('city-create'), data=form_data)

    assert response.status_code == 302
    assert response.url == reverse('city-all-list')  # type: ignore[attr-defined]

    # Проверяем, что город создан
    visited_city = VisitedCity.objects.get(user=setup_db['user'], city=setup_db['city'])
    assert visited_city.user == setup_db['user']
    assert visited_city.city == setup_db['city']
    assert visited_city.date_of_visit == date(2024, 1, 15)
    assert visited_city.rating == 5
    assert visited_city.has_magnet is True
    assert visited_city.impression == 'Great city!'


# pytestmark уже установлен для всего модуля
@patch('city.signals.notify_subscribers_on_city_add')
@patch('city.services.db.set_is_visit_first_for_all_visited_cities')
def test_city_create_without_optional_fields(
    mock_set_first_visit: MagicMock,
    mock_signal: MagicMock,
    setup_db: dict[str, Any],
    client: Client,
) -> None:
    """Проверяет создание города без необязательных полей."""
    client.login(username='testuser', password='testpass')

    form_data = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': setup_db['city'].id,
        'rating': '3',
        'has_magnet': False,
    }

    response = client.post(reverse('city-create'), data=form_data)

    assert response.status_code == 302

    # Проверяем, что город создан
    visited_city = VisitedCity.objects.get(user=setup_db['user'], city=setup_db['city'])
    assert visited_city.date_of_visit is None
    assert visited_city.impression == ''


# pytestmark уже установлен для всего модуля
@patch('city.signals.notify_subscribers_on_city_add')
@patch('city.services.db.set_is_visit_first_for_all_visited_cities')
def test_city_create_user_is_automatically_set(
    mock_set_first_visit: MagicMock,
    mock_signal: MagicMock,
    setup_db: dict[str, Any],
    client: Client,
) -> None:
    """Проверяет, что пользователь автоматически добавляется в форму."""
    client.login(username='testuser', password='testpass')

    form_data = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': setup_db['city'].id,
        'rating': '4',
    }

    response = client.post(reverse('city-create'), data=form_data)

    assert response.status_code == 302

    # Проверяем, что пользователь автоматически установлен
    visited_city = VisitedCity.objects.get(city=setup_db['city'])
    assert visited_city.user == setup_db['user']


# Тесты POST запросов - невалидные данные


# pytestmark уже установлен для всего модуля
def test_city_create_without_required_fields(client: Client) -> None:
    """Проверяет обработку формы без обязательных полей."""
    user = User.objects.create_user(username='testuser', password='testpass')
    client.login(username='testuser', password='testpass')

    # Отправляем форму без обязательных полей
    form_data: dict[str, Any] = {}

    response = client.post(reverse('city-create'), data=form_data)

    # Форма должна вернуться с ошибками (не редирект)
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors


# pytestmark уже установлен для всего модуля
def test_city_create_with_invalid_rating(setup_db: dict[str, Any], client: Client) -> None:
    """Проверяет валидацию рейтинга (должен быть 1-5)."""
    client.login(username='testuser', password='testpass')

    # Пытаемся создать с рейтингом вне диапазона
    form_data = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': setup_db['city'].id,
        'rating': '6',
    }

    response = client.post(reverse('city-create'), data=form_data)

    # Форма должна вернуться с ошибкой
    assert response.status_code == 200
    assert 'form' in response.context
    assert 'rating' in response.context['form'].errors


# pytestmark уже установлен для всего модуля
@patch('city.signals.notify_subscribers_on_city_add')
def test_city_create_duplicate_city_same_date(
    mock_signal: MagicMock,
    setup_db: dict[str, Any],
    client: Client,
) -> None:
    """Проверяет, что нельзя создать дубликат города с той же датой посещения."""
    client.login(username='testuser', password='testpass')

    # Создаем первый посещенный город
    VisitedCity.objects.create(
        user=setup_db['user'],
        city=setup_db['city'],
        date_of_visit=date(2024, 1, 15),
        rating=5,
    )

    # Пытаемся создать дубликат с той же датой
    form_data = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': setup_db['city'].id,
        'date_of_visit': '15.01.2024',
        'rating': '4',
    }

    response = client.post(reverse('city-create'), data=form_data)

    # Форма должна вернуться с ошибкой
    assert response.status_code == 200
    assert 'city' in response.context['form'].errors
    assert 'уже был отмечен Вами как посещённый' in str(response.context['form'].errors['city'])

    # Проверяем, что дубликат не создан
    assert VisitedCity.objects.filter(user=setup_db['user'], city=setup_db['city']).count() == 1


# pytestmark уже установлен для всего модуля
@patch('city.signals.notify_subscribers_on_city_add')
@patch('city.services.db.set_is_visit_first_for_all_visited_cities')
def test_city_create_same_city_different_date_allowed(
    mock_set_first_visit: MagicMock,
    mock_signal: MagicMock,
    setup_db: dict[str, Any],
    client: Client,
) -> None:
    """Проверяет, что можно создать запись для того же города с другой датой."""
    client.login(username='testuser', password='testpass')

    # Создаем первый посещенный город
    VisitedCity.objects.create(
        user=setup_db['user'],
        city=setup_db['city'],
        date_of_visit=date(2024, 1, 15),
        rating=5,
    )

    # Создаем второй с другой датой
    form_data = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': setup_db['city'].id,
        'date_of_visit': '20.02.2024',
        'rating': '4',
    }

    response = client.post(reverse('city-create'), data=form_data)

    # Должен быть успешный редирект
    assert response.status_code == 302

    # Проверяем, что создано 2 записи
    assert VisitedCity.objects.filter(user=setup_db['user'], city=setup_db['city']).count() == 2


# pytestmark уже установлен для всего модуля
@patch('city.signals.notify_subscribers_on_city_add')
def test_city_create_duplicate_without_date(
    mock_signal: MagicMock,
    setup_db: dict[str, Any],
    client: Client,
) -> None:
    """Проверяет, что нельзя создать дубликат города без даты."""
    client.login(username='testuser', password='testpass')

    # Создаем первый посещенный город без даты
    VisitedCity.objects.create(
        user=setup_db['user'],
        city=setup_db['city'],
        date_of_visit=None,
        rating=5,
    )

    # Пытаемся создать дубликат без даты
    form_data = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': setup_db['city'].id,
        'rating': '4',
    }

    response = client.post(reverse('city-create'), data=form_data)

    # Форма должна вернуться с ошибкой
    assert response.status_code == 200
    assert 'city' in response.context['form'].errors
    assert 'уже был отмечен Вами как посещённый без указания даты' in str(
        response.context['form'].errors['city']
    )


# Тесты доступа для POST запросов


# pytestmark уже установлен для всего модуля
def test_city_create_post_guest_redirects_to_login(client: Client) -> None:
    """Проверяет, что неавторизованные пользователи не могут создавать города через POST."""
    form_data: dict[str, Any] = {
        'city': 1,
        'rating': '5',
    }

    response = client.post(reverse('city-create'), data=form_data)

    # Должен быть редирект на страницу входа
    assert response.status_code == 302
    assert '/account/signin' in response.url  # type: ignore[attr-defined]


# Тесты валидации формы


# pytestmark уже установлен для всего модуля
def test_city_create_with_nonexistent_city_id(client: Client) -> None:
    """Проверяет обработку несуществующего city_id в форме."""
    user = User.objects.create_user(username='testuser', password='testpass')
    client.login(username='testuser', password='testpass')

    form_data = {
        'city': 99999,  # Несуществующий город
        'rating': '5',
    }

    response = client.post(reverse('city-create'), data=form_data)

    # Форма должна вернуться с ошибкой
    assert response.status_code == 200
    assert 'form' in response.context
    assert 'city' in response.context['form'].errors


# Тесты на множественные посещения


# pytestmark уже установлен для всего модуля
@patch('city.signals.notify_subscribers_on_city_add')
@patch('city.services.db.set_is_visit_first_for_all_visited_cities')
def test_city_create_multiple_visits_different_cities(
    mock_set_first_visit: MagicMock,
    mock_signal: MagicMock,
    setup_db: dict[str, Any],
    client: Client,
) -> None:
    """Проверяет создание нескольких посещений разных городов."""
    client.login(username='testuser', password='testpass')

    # Создаем два разных города
    city1 = City.objects.create(
        title='City 1',
        country=setup_db['country'],
        region=setup_db['region'],
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )
    city2 = City.objects.create(
        title='City 2',
        country=setup_db['country'],
        region=setup_db['region'],
        coordinate_width=56.8558,
        coordinate_longitude=38.7173,
    )

    # Создаем первое посещение
    form_data1 = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': city1.id,
        'rating': '5',
    }
    response1 = client.post(reverse('city-create'), data=form_data1)
    assert response1.status_code == 302

    # Создаем второе посещение
    form_data2 = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': city2.id,
        'rating': '4',
    }
    response2 = client.post(reverse('city-create'), data=form_data2)
    assert response2.status_code == 302

    # Проверяем, что оба города созданы
    assert VisitedCity.objects.filter(user=setup_db['user']).count() == 2
    assert VisitedCity.objects.filter(user=setup_db['user'], city=city1).exists()
    assert VisitedCity.objects.filter(user=setup_db['user'], city=city2).exists()


# Тесты различных значений рейтинга


# pytestmark уже установлен для всего модуля
@patch('city.signals.notify_subscribers_on_city_add')
@patch('city.services.db.set_is_visit_first_for_all_visited_cities')
def test_city_create_with_all_rating_values(
    mock_set_first_visit: MagicMock,
    mock_signal: MagicMock,
    setup_db: dict[str, Any],
    client: Client,
) -> None:
    """Проверяет создание городов со всеми возможными значениями рейтинга (1-5)."""
    client.login(username='testuser', password='testpass')

    for rating_value in ['1', '2', '3', '4', '5']:
        city = City.objects.create(
            title=f'City {rating_value}',
            country=setup_db['country'],
            region=setup_db['region'],
            coordinate_width=55.0 + float(rating_value),
            coordinate_longitude=37.0 + float(rating_value),
        )

        form_data = {
            'country': setup_db['country'].id,
            'region': setup_db['region'].id,
            'city': city.id,
            'rating': rating_value,
        }

        response = client.post(reverse('city-create'), data=form_data)
        assert response.status_code == 302

        visited_city = VisitedCity.objects.get(user=setup_db['user'], city=city)
        assert visited_city.rating == int(rating_value)


# Тесты проверки логирования


# pytestmark уже установлен для всего модуля
@patch('services.logger.info')
@patch('city.signals.notify_subscribers_on_city_add')
@patch('city.services.db.set_is_visit_first_for_all_visited_cities')
def test_city_create_logs_success(
    mock_set_first_visit: MagicMock,
    mock_signal: MagicMock,
    mock_logger: MagicMock,
    setup_db: dict[str, Any],
    client: Client,
) -> None:
    """Проверяет, что успешное создание города логируется."""
    client.login(username='testuser', password='testpass')

    form_data = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': setup_db['city'].id,
        'rating': '5',
    }

    response = client.post(reverse('city-create'), data=form_data)

    assert response.status_code == 302
    # Проверяем, что логирование было вызвано
    assert mock_logger.called
    assert '(Visited city) Adding a visited city' in str(mock_logger.call_args)


# Тесты на разных пользователей


# pytestmark уже установлен для всего модуля
@patch('city.signals.notify_subscribers_on_city_add')
@patch('city.services.db.set_is_visit_first_for_all_visited_cities')
def test_city_create_different_users_can_add_same_city(
    mock_set_first_visit: MagicMock,
    mock_signal: MagicMock,
    setup_db: dict[str, Any],
    django_user_model: Any,
    client: Client,
) -> None:
    """Проверяет, что разные пользователи могут добавлять один и тот же город."""
    # Создаем второго пользователя
    user2 = django_user_model.objects.create_user(username='testuser2', password='testpass2')

    # Первый пользователь создает город
    client.login(username='testuser', password='testpass')
    form_data = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': setup_db['city'].id,
        'date_of_visit': '15.01.2024',
        'rating': '5',
    }
    response1 = client.post(reverse('city-create'), data=form_data)
    assert response1.status_code == 302

    # Второй пользователь создает тот же город
    client.login(username='testuser2', password='testpass2')
    response2 = client.post(reverse('city-create'), data=form_data)
    assert response2.status_code == 302

    # Проверяем, что оба города созданы
    assert VisitedCity.objects.filter(city=setup_db['city']).count() == 2
    assert VisitedCity.objects.filter(user=setup_db['user'], city=setup_db['city']).exists()
    assert VisitedCity.objects.filter(user=user2, city=setup_db['city']).exists()


# Тесты валидации рейтинга


# pytestmark уже установлен для всего модуля
def test_city_create_with_zero_rating(setup_db: dict[str, Any], client: Client) -> None:
    """Проверяет, что рейтинг 0 не принимается."""
    client.login(username='testuser', password='testpass')

    form_data = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': setup_db['city'].id,
        'rating': '0',
    }

    response = client.post(reverse('city-create'), data=form_data)

    # Форма должна вернуться с ошибкой
    assert response.status_code == 200
    assert 'rating' in response.context['form'].errors


# pytestmark уже установлен для всего модуля
def test_city_create_with_negative_rating(setup_db: dict[str, Any], client: Client) -> None:
    """Проверяет, что отрицательный рейтинг не принимается."""
    client.login(username='testuser', password='testpass')

    form_data = {
        'country': setup_db['country'].id,
        'region': setup_db['region'].id,
        'city': setup_db['city'].id,
        'rating': '-1',
    }

    response = client.post(reverse('city-create'), data=form_data)

    # Форма должна вернуться с ошибкой
    assert response.status_code == 200
    assert 'rating' in response.context['form'].errors
