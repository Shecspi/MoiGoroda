"""
E2E-сценарии страницы генератора изображения «Поделиться прогрессом по региону» (полный рендер).

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""
# mypy: disable-error-code="attr-defined"

from __future__ import annotations

from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from region.models import Region


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.django_db
def test_region_share_page_renders_with_expected_shell(
    client: Client,
    test_user: Any,
    test_region: Region,
    test_city: City,
) -> None:
    """Авторизованный пользователь получает полную HTML-страницу share с ключевым контентом."""
    VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

    client.force_login(test_user)
    response = client.get(reverse('region-share', kwargs={'pk': test_region.pk}))

    assert response.status_code == 200
    assert 'region/selected/share/page.html' in [t.name for t in response.templates]
    body = response.content.decode('utf-8')
    assert 'Поделиться прогрессом по региону' in body
    assert str(test_region.pk) in body or test_region.full_name in body


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.django_db
def test_region_share_workflow_from_list_to_share_image_page(
    client: Client,
    test_user: Any,
    test_country: Any,
    test_region: Region,
) -> None:
    """Сценарий: список городов региона → страница share с данными в контексте."""
    city = City.objects.create(
        title='E2E-город',
        region=test_region,
        country=test_country,
        coordinate_width=55.1,
        coordinate_longitude=37.2,
    )
    VisitedCity.objects.create(user=test_user, city=city, rating=5)

    client.force_login(test_user)

    list_resp = client.get(reverse('region-selected-list', kwargs={'pk': test_region.pk}))
    assert list_resp.status_code == 200

    share_resp = client.get(reverse('region-share', kwargs={'pk': test_region.pk}))
    assert share_resp.status_code == 200
    assert share_resp.context['region_id'] == test_region.pk
    assert share_resp.context['number_of_cities'] >= 1
    assert share_resp.context['number_of_visited_cities'] >= 1
    assert any(
        c['coordinate_width'] == 55.1 and c['coordinate_longitude'] == 37.2
        for c in share_resp.context['all_cities']
    )


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.django_db
def test_region_share_anonymous_redirect_then_login_can_open_share(
    client: Client,
    test_user: Any,
    test_region: Region,
) -> None:
    """Гость перенаправляется на вход; после входа страница share открывается."""
    url = reverse('region-share', kwargs={'pk': test_region.pk})
    r1 = client.get(url)
    assert r1.status_code == 302

    client.force_login(test_user)
    r2 = client.get(url)
    assert r2.status_code == 200
