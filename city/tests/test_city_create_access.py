"""
Тесты доступа к странице создания города.

Покрывает:
- Доступ неавторизованных пользователей (редирект на страницу входа)
- Доступ авторизованных пользователей
- Проверку шаблонов и статус-кодов

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


# Фикстуры


@pytest.fixture
@pytest.mark.django_db
def test_user() -> User:
    """Фикстура для создания тестового пользователя."""
    return User.objects.create_user(username='testuser', password='testpass')


# Тесты доступа


@pytest.mark.django_db
def test_city_create_guest_access_redirects_to_login(client: Client) -> None:
    """Проверяет, что неавторизованные пользователи перенаправляются на страницу входа."""
    response = client.get(reverse('city-create'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_city_create_guest_access_shows_login_template(client: Client) -> None:
    """Проверяет, что неавторизованные пользователи видят страницу входа после редиректа."""
    response = client.get(reverse('city-create'), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_city_create_authenticated_user_access(test_user: User, client: Client) -> None:
    """Проверяет, что авторизованные пользователи имеют доступ к странице создания города."""
    client.login(username='testuser', password='testpass')
    response = client.get(reverse('city-create'))

    assert response.status_code == 200
    assert 'city/city_create.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_city_create_page_context(test_user: User, client: Client) -> None:
    """Проверяет контекст страницы создания города."""
    client.login(username='testuser', password='testpass')
    response = client.get(reverse('city-create'))

    assert response.context['action'] == 'create'
    assert response.context['active_page'] == 'add_city'
    assert response.context['page_title'] == 'Добавление города'
    assert response.context['page_description'] == 'Добавление нового посещённого города'


@pytest.mark.django_db
def test_city_create_with_valid_city_id_parameter(test_user: User, client: Client) -> None:
    """Проверяет предзаполнение формы при передаче валидного city_id."""
    from country.models import Country
    from city.models import City

    # Создаем тестовые данные
    country = Country.objects.create(name='Test Country', code='TC')
    city = City.objects.create(
        title='Test City',
        country=country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )

    client.login(username='testuser', password='testpass')
    response = client.get(reverse('city-create') + f'?city_id={city.id}')

    assert response.status_code == 200
    assert response.context['form'].initial['city'] == city.id
    assert response.context['form'].initial['country'] == country.id


@pytest.mark.django_db
def test_city_create_with_invalid_city_id_parameter(test_user: User, client: Client) -> None:
    """Проверяет обработку невалидного city_id (не число)."""
    client.login(username='testuser', password='testpass')
    response = client.get(reverse('city-create') + '?city_id=invalid')

    assert response.status_code == 200
    # Форма должна загрузиться без предзаполнения
    assert 'city' not in response.context['form'].initial


@pytest.mark.django_db
def test_city_create_with_nonexistent_city_id_parameter(test_user: User, client: Client) -> None:
    """Проверяет обработку несуществующего city_id."""
    client.login(username='testuser', password='testpass')
    response = client.get(reverse('city-create') + '?city_id=99999')

    assert response.status_code == 200
    # Форма должна загрузиться без предзаполнения
    assert 'city' not in response.context['form'].initial


# Тесты структуры формы


@pytest.mark.django_db
def test_city_create_form_has_all_required_fields(test_user: User, client: Client) -> None:
    """Проверяет наличие всех обязательных полей в форме."""
    client.login(username='testuser', password='testpass')
    response = client.get(reverse('city-create'))

    form = response.context['form']

    # Проверяем наличие всех полей
    assert 'country' in form.fields
    assert 'region' in form.fields
    assert 'city' in form.fields
    assert 'date_of_visit' in form.fields
    assert 'rating' in form.fields
    assert 'has_magnet' in form.fields
    assert 'impression' in form.fields


@pytest.mark.django_db
def test_city_create_form_field_properties(test_user: User, client: Client) -> None:
    """Проверяет свойства полей формы."""
    client.login(username='testuser', password='testpass')
    response = client.get(reverse('city-create'))

    form = response.context['form']

    # impression должно быть необязательным
    assert form.fields['impression'].required is False

    # rating должен иметь choices от 1 до 5
    rating_choices = list(form.fields['rating'].choices)
    assert len(rating_choices) == 5
    assert ('1', '1') in rating_choices
    assert ('5', '5') in rating_choices

    # country и city должны быть обязательными
    assert form.fields['country'].required is True
    assert form.fields['city'].required is True
