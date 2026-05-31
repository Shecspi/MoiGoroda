from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


@pytest.mark.integration
@pytest.mark.django_db
def test_geo_polygons_page_renders_for_anonymous(client: Client) -> None:
    response = client.get(reverse('geo-polygons'))

    assert response.status_code == 200
    assert 'geo_polygons/page.html' in (template.name for template in response.templates)
    content = response.content.decode()
    assert 'Полигоны OpenStreetMap' in content
    assert 'id="geo-viewer"' in content
    assert 'id="download-btn"' in content
    assert 'id="clear-btn"' in content
    assert 'window.OSM_VIEWER_IS_AUTHENTICATED = false' in content
    assert 'window.OSM_VIEWER_HAS_ADVANCED_PREMIUM = false' in content


@pytest.mark.integration
@pytest.mark.django_db
def test_geo_polygons_page_context_for_authenticated_user(client: Client, user: User) -> None:
    client.force_login(user)

    response = client.get(reverse('geo-polygons'))

    assert response.status_code == 200
    assert response.context['page_title'] == 'Полигоны OpenStreetMap'
    assert response.context['active_page'] == 'geo_polygons'
    content = response.content.decode()
    assert 'window.OSM_VIEWER_IS_AUTHENTICATED = true' in content
    assert 'window.OSM_VIEWER_HAS_ADVANCED_PREMIUM = false' in content


@pytest.mark.integration
@pytest.mark.django_db
def test_geo_polygons_page_shows_advanced_premium_flag(
    client: Client,
    premium_user: User,
) -> None:
    client.force_login(premium_user)

    response = client.get(reverse('geo-polygons'))

    assert response.status_code == 200
    assert 'window.OSM_VIEWER_HAS_ADVANCED_PREMIUM = true' in response.content.decode()
