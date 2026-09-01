# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Интеграционные тесты контекста общих коллекций города."""

from typing import Any

import pytest
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext

from city.models import City
from collection.models import Collection, PersonalCollection
from collection.services import get_city_collection_context
from country.models import Country
from region.models import Region


@pytest.fixture
def city(region_type: Any) -> City:
    country = Country.objects.create(name='Россия', code='RU')
    region = Region.objects.create(
        title='Тверская область',
        country=country,
        type=region_type,
        iso3166='RU-TVE',
        full_name='Тверская область',
    )
    return City.objects.create(
        title='<Тверь>',
        region=region,
        country=country,
        coordinate_width=56.8587,
        coordinate_longitude=35.9176,
    )


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize('common_count', [0, 1, 3])
def test_city_collection_context_has_constant_query_count_and_expected_dto(
    city: City,
    common_count: int,
) -> None:
    collections = [Collection.objects.create(title=f'Коллекция {index}') for index in range(3)]
    for collection in collections[:common_count]:
        collection.city.add(city)

    with CaptureQueriesContext(connection) as queries:
        context = get_city_collection_context(city)

    assert len(queries) == 1
    assert 'OVER ()' in queries[0]['sql']
    assert 'ORDER BY 2 ASC' in queries[0]['sql']
    assert context == {
        'city': {
            'id': city.id,
            'title': '<Тверь>',
            'url': f'/city/{city.id}',
        },
        'common_collections': {
            'count': common_count,
            'single': (
                {
                    'id': collections[0].id,
                    'title': 'Коллекция 0',
                    'url': f'/collection/{collections[0].id}/list',
                }
                if common_count == 1
                else None
            ),
            'catalog_url': f'/collection/?city={city.id}',
        },
    }


@pytest.mark.django_db
@pytest.mark.integration
def test_city_collection_context_excludes_private_and_public_personal_collections(
    city: City,
) -> None:
    common = Collection.objects.create(title='<Общая>')
    common.city.add(city)
    user = User.objects.create_user(username='owner')
    private = PersonalCollection.objects.create(title='Личная', user=user, is_public=False)
    public = PersonalCollection.objects.create(title='Публичная личная', user=user, is_public=True)
    private.city.add(city)
    public.city.add(city)

    context = get_city_collection_context(city)

    assert context['common_collections']['count'] == 1
    assert context['common_collections']['single'] == {
        'id': common.id,
        'title': '<Общая>',
        'url': f'/collection/{common.id}/list',
    }
