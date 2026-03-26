import pytest
from typing import Any

from django.test import Client
from django.urls import reverse


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_requires_authentication(client: Client) -> None:
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    assert '/account/signin' in str(response.url)  # type: ignore[attr-defined]


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_denies_non_superuser(client: Client, django_user_model: Any) -> None:
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    client.force_login(user)
    response = client.get(reverse('dashboard'))
    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_allows_superuser(client: Client, django_user_model: Any) -> None:
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')
    client.force_login(superuser)
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert 'dashboard/dashboard.html' in [t.name for t in response.templates]
    assert response.context['page_title'] == 'Dashboard'
