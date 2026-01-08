"""
Тесты для API get_visit_years.

Покрывает:
- Аутентификацию и права доступа
- HTTP методы (разрешенные и запрещенные)
- Получение списка годов посещений
- Фильтрацию по стране
- Обработку несуществующей страны
- Логирование
- Уникальность и сортировку годов

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import date
from typing import Type
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from city.models import City, VisitedCity
from country.models import Country

VISIT_YEARS_URL = reverse('api__get_visit_years')


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


@pytest.fixture
def test_country(db) -> Country:  # type: ignore[no-untyped-def]
    """Создает тестовую страну."""
    return Country.objects.create(name='Russia', code='RU', fullname='Russian Federation')


@pytest.fixture
def test_city(test_country: Country, db) -> City:  # type: ignore[no-untyped-def]
    """Создает тестовый город."""
    return City.objects.create(
        title='Moscow',
        country=test_country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )


# Тесты доступа и методов


@pytest.mark.integration
def test_get_visit_years_guest_cannot_access(api_client: APIClient) -> None:
    """Проверяет, что гость не может получить доступ к API."""
    response = api_client.get(VISIT_YEARS_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert 'detail' in data
    assert 'авторизован' in data['detail'].lower()


@pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
@pytest.mark.integration
def test_get_visit_years_prohibited_methods(
    api_client: APIClient, authenticated_user: User, method: str
) -> None:
    """Проверяет, что запрещенные методы возвращают 405."""
    client_method = getattr(api_client, method)
    response = client_method(VISIT_YEARS_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# Тесты получения данных


@pytest.mark.integration
def test_get_visit_years_empty_list(api_client: APIClient, authenticated_user: User) -> None:
    """Проверяет, что API возвращает пустой список, если посещений нет."""
    response = api_client.get(VISIT_YEARS_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'years' in data
    assert data['years'] == []


@pytest.mark.integration
def test_get_visit_years_single_year(
    api_client: APIClient, authenticated_user: User, test_city: City
) -> None:
    """Проверяет получение одного года посещений."""
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=date(2024, 1, 15),
        rating=3,
    )

    response = api_client.get(VISIT_YEARS_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'years' in data
    assert data['years'] == [2024]


@pytest.mark.integration
def test_get_visit_years_multiple_years_sorted(
    api_client: APIClient, authenticated_user: User, test_city: City
) -> None:
    """Проверяет получение нескольких годов в порядке убывания."""
    # Создаём посещения в разные годы (не в хронологическом порядке)
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=date(2022, 6, 1),
        rating=3,
    )
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=date(2024, 1, 15),
        rating=3,
    )
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=date(2023, 8, 20),
        rating=3,
    )

    response = api_client.get(VISIT_YEARS_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'years' in data
    # Годы должны быть отсортированы по убыванию
    assert data['years'] == [2024, 2023, 2022]


@pytest.mark.integration
def test_get_visit_years_unique_years(
    api_client: APIClient, authenticated_user: User, test_city: City
) -> None:
    """Проверяет, что одинаковые годы не дублируются."""
    # Создаём несколько посещений в один год
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=date(2024, 1, 15),
        rating=3,
    )
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=date(2024, 6, 20),
        rating=3,
    )
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=date(2024, 12, 31),
        rating=3,
    )

    response = api_client.get(VISIT_YEARS_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'years' in data
    # 2024 должен быть только один раз
    assert data['years'] == [2024]
    assert len(data['years']) == 1


@pytest.mark.integration
def test_get_visit_years_excludes_null_dates(
    api_client: APIClient, authenticated_user: User, test_city: City
) -> None:
    """Проверяет, что записи без даты посещения не учитываются."""
    # Создаём посещение с датой
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=date(2024, 1, 15),
        rating=3,
    )
    # Создаём посещение без даты (должно быть проигнорировано)
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=None,
        rating=3,
    )

    response = api_client.get(VISIT_YEARS_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'years' in data
    # Должен быть только 2024, запись без даты не учитывается
    assert data['years'] == [2024]


@pytest.mark.integration
def test_get_visit_years_filter_by_country(
    api_client: APIClient,
    authenticated_user: User,
    test_country: Country,
    test_city: City,
) -> None:
    """Проверяет фильтрацию годов по стране."""
    # Создаём другую страну и город
    other_country = Country.objects.create(name='USA', code='US', fullname='United States')
    other_city = City.objects.create(
        title='New York',
        country=other_country,
        coordinate_width=40.7128,
        coordinate_longitude=-74.0060,
    )

    # Посещения в разных странах
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,  # Россия
        date_of_visit=date(2024, 1, 15),
        rating=3,
    )
    VisitedCity.objects.create(
        user=authenticated_user,
        city=other_city,  # США
        date_of_visit=date(2023, 6, 10),
        rating=3,
    )

    # Без фильтра должны быть оба года
    response = api_client.get(VISIT_YEARS_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert set(data['years']) == {2024, 2023}

    # С фильтром по России должен быть только 2024
    response = api_client.get(VISIT_YEARS_URL, {'country': 'RU'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['years'] == [2024]

    # С фильтром по США должен быть только 2023
    response = api_client.get(VISIT_YEARS_URL, {'country': 'US'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['years'] == [2023]


@pytest.mark.integration
def test_get_visit_years_country_not_found(api_client: APIClient, authenticated_user: User) -> None:
    """Проверяет обработку несуществующей страны."""
    response = api_client.get(VISIT_YEARS_URL, {'country': 'XX'})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert 'detail' in data
    assert 'не найдена' in data['detail'].lower()
    assert 'XX' in data['detail']


@pytest.mark.integration
def test_get_visit_years_multiple_cities_same_year(
    api_client: APIClient,
    authenticated_user: User,
    test_country: Country,
) -> None:
    """Проверяет, что посещения разных городов в один год учитываются правильно."""
    city1 = City.objects.create(
        title='Moscow',
        country=test_country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )
    city2 = City.objects.create(
        title='Saint Petersburg',
        country=test_country,
        coordinate_width=59.9343,
        coordinate_longitude=30.3351,
    )

    # Посещения разных городов в один год
    VisitedCity.objects.create(
        user=authenticated_user,
        city=city1,
        date_of_visit=date(2024, 1, 15),
        rating=3,
    )
    VisitedCity.objects.create(
        user=authenticated_user,
        city=city2,
        date_of_visit=date(2024, 6, 20),
        rating=3,
    )

    response = api_client.get(VISIT_YEARS_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'years' in data
    # 2024 должен быть только один раз, несмотря на несколько городов
    assert data['years'] == [2024]
    assert len(data['years']) == 1


@pytest.mark.integration
def test_get_visit_years_only_current_user(
    api_client: APIClient,
    authenticated_user: User,
    test_city: City,
    django_user_model: Type[User],
) -> None:
    """Проверяет, что возвращаются только годы посещений текущего пользователя."""
    # Создаём другого пользователя
    other_user = django_user_model.objects.create_user(username='otheruser', password='pass')

    # Посещения текущего пользователя
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=date(2024, 1, 15),
        rating=3,
    )
    # Посещения другого пользователя (не должны учитываться)
    VisitedCity.objects.create(
        user=other_user,
        city=test_city,
        date_of_visit=date(2023, 6, 10),
        rating=3,
    )

    response = api_client.get(VISIT_YEARS_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'years' in data
    # Должен быть только 2024 (год посещения текущего пользователя)
    assert data['years'] == [2024]
    assert 2023 not in data['years']


# Тесты логирования


@patch('city.api.logger')
@pytest.mark.integration
def test_get_visit_years_logs_successful_request(
    mock_logger: MagicMock,
    api_client: APIClient,
    authenticated_user: User,
    test_city: City,
) -> None:
    """Проверяет, что успешный запрос логируется."""
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=date(2024, 1, 15),
        rating=3,
    )

    response = api_client.get(VISIT_YEARS_URL)
    assert response.status_code == status.HTTP_200_OK

    mock_logger.info.assert_called_once()
    args, kwargs = mock_logger.info.call_args
    # Проверяем, что в логе есть ID пользователя
    assert 'user #' in args[1]
    assert str(authenticated_user.id) in args[1]
    # Проверяем, что в логе указано "all" для страны (без фильтра)
    assert 'country: all' in args[1]
    # Проверяем, что в логе указано количество годов
    assert 'years count: 1' in args[1]


@patch('city.api.logger')
@pytest.mark.integration
def test_get_visit_years_logs_with_country_filter(
    mock_logger: MagicMock,
    api_client: APIClient,
    authenticated_user: User,
    test_country: Country,
    test_city: City,
) -> None:
    """Проверяет логирование запроса с фильтром по стране."""
    VisitedCity.objects.create(
        user=authenticated_user,
        city=test_city,
        date_of_visit=date(2024, 1, 15),
        rating=3,
    )

    response = api_client.get(VISIT_YEARS_URL, {'country': 'RU'})
    assert response.status_code == status.HTTP_200_OK

    mock_logger.info.assert_called_once()
    args, kwargs = mock_logger.info.call_args
    # Проверяем, что в логе указан код страны
    assert 'country: RU' in args[1]
