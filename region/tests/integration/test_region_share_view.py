"""
Тесты RegionShareView — страница генератора изображения «Поделиться прогрессом по региону».

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""
# mypy: disable-error-code="attr-defined"

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from region.models import Region


def _context_from_render(mock_render: MagicMock) -> dict[str, Any]:
    _request, _template, context = mock_render.call_args[0]
    return context


def _patch_render_ok(mock_render: MagicMock) -> None:
    """HttpResponse нужен, иначе middleware (сессии и т.д.) падают на заголовках."""
    mock_render.return_value = HttpResponse()


@pytest.mark.integration
@pytest.mark.django_db
@patch('region.views.render')
def test_region_share_anonymous_redirects_to_login_with_next(
    mock_render: MagicMock,
    client: Client,
    test_region: Region,
) -> None:
    """Неавторизованный пользователь перенаправляется на вход; next указывает на страницу share."""
    url = reverse('region-share', kwargs={'pk': test_region.pk})
    response = client.get(url)

    assert response.status_code == 302
    assert settings.LOGIN_URL in response.url
    parsed = urlparse(response.url)
    next_vals = parse_qs(parsed.query).get('next', [])
    assert next_vals and next_vals[0] == url
    mock_render.assert_not_called()


@pytest.mark.integration
@pytest.mark.django_db
@patch('region.views.render')
def test_region_share_authenticated_404_when_region_missing(
    mock_render: MagicMock,
    client: Client,
    test_user: Any,
) -> None:
    """Несуществующий регион — 404, render не вызывается."""
    client.force_login(test_user)
    response = client.get(reverse('region-share', kwargs={'pk': 999_999}))

    assert response.status_code == 404
    mock_render.assert_not_called()


@pytest.mark.integration
@pytest.mark.django_db
@patch('region.views.render')
def test_region_share_context_empty_region(
    mock_render: MagicMock,
    client: Client,
    test_user: Any,
    test_country: Any,
    test_region_type: Any,
    test_area: Any,
) -> None:
    """Регион без городов: нули и пустой список городов."""
    _patch_render_ok(mock_render)
    empty_region = Region.objects.create(
        title='Пустой',
        full_name='Пустой регион',
        country=test_country,
        type=test_region_type,
        area=test_area,
        iso3166='RU-XXX',
    )
    client.force_login(test_user)
    response = client.get(reverse('region-share', kwargs={'pk': empty_region.pk}))

    assert response.status_code == 200
    mock_render.assert_called_once()
    ctx = _context_from_render(mock_render)
    assert ctx['region_id'] == empty_region.pk
    assert ctx['number_of_cities'] == 0
    assert ctx['number_of_visited_cities'] == 0
    assert ctx['all_cities'] == []
    assert ctx['region_name'] == empty_region.full_name
    assert ctx['country_name'] == str(test_country)
    assert ctx['iso3166_code'] == 'RU-XXX'
    assert 'Создание изображения региона' in ctx['page_title']
    assert empty_region.full_name in ctx['page_description']


@pytest.mark.integration
@pytest.mark.django_db
@patch('region.views.render')
def test_region_share_context_counts_visited_and_structure(
    mock_render: MagicMock,
    client: Client,
    test_user: Any,
    test_country: Any,
    test_region: Region,
) -> None:
    """Несколько городов; посещённые учитываются; у каждой записи нужные поля."""
    c1 = City.objects.create(
        title='A',
        region=test_region,
        country=test_country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )
    City.objects.create(
        title='B',
        region=test_region,
        country=test_country,
        coordinate_width=56.0,
        coordinate_longitude=38.0,
    )
    c3 = City.objects.create(
        title='C',
        region=test_region,
        country=test_country,
        coordinate_width=57.0,
        coordinate_longitude=39.0,
    )
    VisitedCity.objects.create(user=test_user, city=c1, rating=5)
    VisitedCity.objects.create(user=test_user, city=c3, rating=4)

    _patch_render_ok(mock_render)
    client.force_login(test_user)
    response = client.get(reverse('region-share', kwargs={'pk': test_region.pk}))

    assert response.status_code == 200
    ctx = _context_from_render(mock_render)
    assert ctx['number_of_cities'] == 3
    assert ctx['number_of_visited_cities'] == 2

    # values() не включает title — проверяем координаты и флаги
    coords = {(c['coordinate_width'], c['coordinate_longitude']): c for c in ctx['all_cities']}
    assert len(coords) == 3
    assert coords[(55.0, 37.0)]['is_visited'] is True
    assert coords[(56.0, 38.0)]['is_visited'] is False
    assert coords[(57.0, 39.0)]['is_visited'] is True


@pytest.mark.integration
@pytest.mark.django_db
@patch('region.views.render')
def test_region_share_excludes_cities_from_other_regions(
    mock_render: MagicMock,
    client: Client,
    test_user: Any,
    test_country: Any,
    test_region: Region,
    test_region_type: Any,
    test_area: Any,
) -> None:
    """В выборку попадают только города указанного региона."""
    other = Region.objects.create(
        title='Другой',
        full_name='Другой регион',
        country=test_country,
        type=test_region_type,
        area=test_area,
        iso3166='RU-OTH',
    )
    City.objects.create(
        title='В чужом регионе',
        region=other,
        country=test_country,
        coordinate_width=60.0,
        coordinate_longitude=40.0,
    )
    City.objects.create(
        title='В нашем',
        region=test_region,
        country=test_country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )

    _patch_render_ok(mock_render)
    client.force_login(test_user)
    response = client.get(reverse('region-share', kwargs={'pk': test_region.pk}))

    assert response.status_code == 200
    ctx = _context_from_render(mock_render)
    assert ctx['number_of_cities'] == 1
    assert len(ctx['all_cities']) == 1


@pytest.mark.integration
@pytest.mark.django_db
@patch('region.views.render')
def test_region_share_duplicate_visit_rows_count_one_visited_city(
    mock_render: MagicMock,
    client: Client,
    test_user: Any,
    test_region: Region,
    test_city: City,
) -> None:
    """Несколько записей VisitedCity по одному городу не увеличивают число «посещённых городов»."""
    from datetime import date

    VisitedCity.objects.create(
        user=test_user, city=test_city, rating=5, date_of_visit=date(2023, 1, 1)
    )
    VisitedCity.objects.create(
        user=test_user, city=test_city, rating=5, date_of_visit=date(2024, 6, 1)
    )

    _patch_render_ok(mock_render)
    client.force_login(test_user)
    response = client.get(reverse('region-share', kwargs={'pk': test_region.pk}))

    assert response.status_code == 200
    ctx = _context_from_render(mock_render)
    assert ctx['number_of_cities'] == 1
    assert ctx['number_of_visited_cities'] == 1
    assert ctx['all_cities'][0]['is_visited'] is True


@pytest.mark.integration
@pytest.mark.django_db
@patch('region.views.render')
def test_region_share_other_user_visits_do_not_affect_flags(
    mock_render: MagicMock,
    client: Client,
    test_user: Any,
    test_region: Region,
    test_city: City,
) -> None:
    """Посещения другого пользователя не помечают город посещённым для текущего."""
    other = User.objects.create_user(username='other', password='x')
    VisitedCity.objects.create(user=other, city=test_city, rating=5)

    _patch_render_ok(mock_render)
    client.force_login(test_user)
    response = client.get(reverse('region-share', kwargs={'pk': test_region.pk}))

    assert response.status_code == 200
    ctx = _context_from_render(mock_render)
    assert ctx['number_of_visited_cities'] == 0
    assert ctx['all_cities'][0]['is_visited'] is False


@pytest.mark.integration
@pytest.mark.django_db
@patch('region.views.render')
def test_region_share_all_visited(
    mock_render: MagicMock,
    client: Client,
    test_user: Any,
    test_country: Any,
    test_region: Region,
) -> None:
    """Все города региона посещены."""
    c1 = City.objects.create(
        title='X',
        region=test_region,
        country=test_country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )
    c2 = City.objects.create(
        title='Y',
        region=test_region,
        country=test_country,
        coordinate_width=56.0,
        coordinate_longitude=38.0,
    )
    VisitedCity.objects.create(user=test_user, city=c1, rating=5)
    VisitedCity.objects.create(user=test_user, city=c2, rating=5)

    _patch_render_ok(mock_render)
    client.force_login(test_user)
    response = client.get(reverse('region-share', kwargs={'pk': test_region.pk}))

    assert response.status_code == 200
    ctx = _context_from_render(mock_render)
    assert ctx['number_of_cities'] == 2
    assert ctx['number_of_visited_cities'] == 2
    assert all(c['is_visited'] for c in ctx['all_cities'])


@pytest.mark.integration
@pytest.mark.django_db
@patch('region.views.render')
def test_region_share_uses_share_template(
    mock_render: MagicMock,
    client: Client,
    test_user: Any,
    test_region: Region,
) -> None:
    """Передан корректный шаблон."""
    _patch_render_ok(mock_render)
    client.force_login(test_user)
    client.get(reverse('region-share', kwargs={'pk': test_region.pk}))

    _request, template_name, _ctx = mock_render.call_args[0]
    assert template_name == 'region/selected/share/page.html'


@pytest.mark.integration
@pytest.mark.django_db
def test_region_share_post_method_not_allowed(
    client: Client,
    test_user: Any,
    test_region: Region,
) -> None:
    """Разрешён только GET."""
    client.force_login(test_user)
    response = client.post(reverse('region-share', kwargs={'pk': test_region.pk}))

    assert response.status_code == 405


@pytest.mark.integration
@pytest.mark.django_db
@patch('region.views.render')
def test_region_share_all_cities_unvisited(
    mock_render: MagicMock,
    client: Client,
    test_user: Any,
    test_country: Any,
    test_region: Region,
) -> None:
    """Города есть, но пользователь ничего не посещал — все is_visited False."""
    City.objects.create(
        title='Solo',
        region=test_region,
        country=test_country,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )

    _patch_render_ok(mock_render)
    client.force_login(test_user)
    response = client.get(reverse('region-share', kwargs={'pk': test_region.pk}))

    assert response.status_code == 200
    ctx = _context_from_render(mock_render)
    assert ctx['number_of_cities'] == 1
    assert ctx['number_of_visited_cities'] == 0
    assert ctx['all_cities'][0]['is_visited'] is False


@pytest.mark.integration
@pytest.mark.django_db
def test_region_share_redirects_when_trailing_slash_missing(
    client: Client,
    test_user: Any,
    test_region: Region,
) -> None:
    """CommonMiddleware перенаправляет на URL со слешем в конце."""
    client.force_login(test_user)
    path = reverse('region-share', kwargs={'pk': test_region.pk})
    assert path.endswith('/')
    no_slash = path.rstrip('/')
    response = client.get(no_slash)

    assert response.status_code == 301
    assert response.url.endswith(path)
