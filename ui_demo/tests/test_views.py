import pytest
from typing import Any

from django.test import Client, override_settings
from django.urls import reverse


@pytest.mark.integration
@pytest.mark.django_db
def test_ui_demo_requires_login(client: Client) -> None:
    with override_settings(DEBUG=True):
        response = client.get(reverse('ui_demo:index'))
    assert response.status_code == 302
    assert '/account/signin' in str(response.url)  # type: ignore[attr-defined]


@pytest.mark.integration
@pytest.mark.django_db
def test_ui_demo_denies_non_superuser(client: Client, django_user_model: Any) -> None:
    user = django_user_model.objects.create_user(username='u1', password='p')
    client.force_login(user)
    with override_settings(DEBUG=True):
        response = client.get(reverse('ui_demo:index'))
    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.django_db
def test_ui_demo_returns_404_when_debug_false(client: Client, django_user_model: Any) -> None:
    admin = django_user_model.objects.create_superuser(username='a', email='a@a.com', password='p')
    client.force_login(admin)
    with override_settings(DEBUG=False):
        response = client.get(reverse('ui_demo:index'))
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
def test_ui_demo_allows_superuser_when_debug(client: Client, django_user_model: Any) -> None:
    admin = django_user_model.objects.create_superuser(username='a', email='a@a.com', password='p')
    client.force_login(admin)
    with override_settings(DEBUG=True):
        response = client.get(reverse('ui_demo:index'))
    assert response.status_code == 200
    assert response.context['active_page'] == 'ui_demo'
    assert response.context['page_title'] == 'UI kit (демо)'

    with override_settings(DEBUG=True):
        r2 = client.get(reverse('ui_demo:buttons'))
    assert r2.status_code == 200
