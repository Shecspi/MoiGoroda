import pytest
from typing import Any

from django.test import Client


API_PATHS = [
    '/api/dashboard/users/overview/',
    '/api/dashboard/visited_cities/overview/',
    '/api/dashboard/visited_countries/overview/',
    '/api/dashboard/places/overview/',
    '/api/dashboard/places/personal_collections/overview/',
    '/api/dashboard/blog/articles/overview/',
]


@pytest.mark.integration
@pytest.mark.django_db
@pytest.mark.parametrize('path', API_PATHS)
def test_dashboard_api_returns_401_for_anonymous(client: Client, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 401
    assert response.json()['detail'] == 'Access restricted to administrators only.'


@pytest.mark.integration
@pytest.mark.django_db
@pytest.mark.parametrize('path', API_PATHS)
def test_dashboard_api_returns_401_for_non_superuser(
    client: Client, django_user_model: Any, path: str
) -> None:
    user = django_user_model.objects.create_user(username='regular', password='pass')
    client.force_login(user)
    response = client.get(path)
    assert response.status_code == 401
    assert response.json()['detail'] == 'Access restricted to administrators only.'


@pytest.mark.integration
@pytest.mark.django_db
@pytest.mark.parametrize('path', API_PATHS)
def test_dashboard_api_returns_200_for_superuser(
    client: Client, django_user_model: Any, path: str
) -> None:
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')
    client.force_login(superuser)
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.django_db
def test_users_overview_last_6m_weekly_chart_has_non_zero_data(
    client: Client, django_user_model: Any
) -> None:
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')
    django_user_model.objects.create_user(username='week_user_1', password='pass')
    django_user_model.objects.create_user(username='week_user_2', password='pass')

    client.force_login(superuser)
    response = client.get('/api/dashboard/users/overview/')

    assert response.status_code == 200
    chart = response.json()['registrations_last_6m']['chart']
    assert len(chart) > 0
    assert any(item['count'] > 0 for item in chart)
