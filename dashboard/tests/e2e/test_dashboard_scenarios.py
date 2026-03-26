import pytest
from typing import Any

from django.test import Client
from django.urls import reverse


@pytest.mark.e2e
@pytest.mark.django_db
def test_dashboard_access_flow(client: Client, django_user_model: Any) -> None:
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302

    regular_user = django_user_model.objects.create_user(username='regular', password='pass')
    client.force_login(regular_user)
    response = client.get(reverse('dashboard'))
    assert response.status_code == 403

    client.logout()
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')
    client.force_login(superuser)
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert response.context['page_title'] == 'Dashboard'


@pytest.mark.e2e
@pytest.mark.django_db
def test_dashboard_api_flow(client: Client, django_user_model: Any) -> None:
    endpoint = '/api/dashboard/users/overview/'

    response = client.get(endpoint)
    assert response.status_code == 401

    regular_user = django_user_model.objects.create_user(username='regular', password='pass')
    client.force_login(regular_user)
    response = client.get(endpoint)
    assert response.status_code == 401

    client.logout()
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')
    client.force_login(superuser)
    response = client.get(endpoint)
    assert response.status_code == 200
