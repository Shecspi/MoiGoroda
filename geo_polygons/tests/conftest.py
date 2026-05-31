from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal
from typing import Any, cast

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.utils import timezone

from geo_polygons.domain.entities import OSMPolygon
from geo_polygons.infrastructure.models import OSMPolygonCache
from premium.models import PremiumPlan, PremiumSubscription

RELATION_ID = 123
POLYGON_GEOMETRY = {
    'type': 'Polygon',
    'coordinates': [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 0.0]]],
}


def response_json(response: Any) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(response.content.decode()))


def make_polygon(
    *,
    relation_id: int = RELATION_ID,
    name: str = 'Moscow Oblast',
    geometry: dict[str, Any] | None = None,
) -> OSMPolygon:
    return OSMPolygon(
        relation_id=relation_id,
        name=name,
        geometry=geometry or POLYGON_GEOMETRY,
    )


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def user(django_user_model: type[User]) -> User:
    return django_user_model.objects.create_user(username='geo_user', password='pass')


@pytest.fixture
def advanced_plan() -> PremiumPlan:
    return PremiumPlan.objects.create(
        slug='advanced',
        name='Advanced',
        description='Advanced plan',
        price_month=Decimal('599.00'),
        price_year=Decimal('5990.00'),
        currency='RUB',
        is_active=True,
        sort_order=0,
    )


@pytest.fixture
def premium_user(user: User, advanced_plan: PremiumPlan) -> User:
    now = timezone.now()
    PremiumSubscription.objects.create(
        user=user,
        plan=advanced_plan,
        billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
        status=PremiumSubscription.Status.ACTIVE,
        started_at=now,
        expires_at=now + timedelta(days=30),
        provider_payment_id='geo-polygon-test-payment',
    )
    return user


@pytest.fixture
def cached_polygon(db: None) -> OSMPolygonCache:
    return OSMPolygonCache.objects.create(
        relation_id=RELATION_ID,
        name='Moscow Oblast',
        geojson=POLYGON_GEOMETRY,
    )


@pytest.fixture
def mock_polygon_service(mocker: Any) -> Any:
    service = mocker.Mock()
    service.execute.return_value = None

    def configure(polygon: OSMPolygon | None) -> None:
        service.execute.return_value = polygon

    service.configure = configure
    mocker.patch('geo_polygons.api._get_polygon_service', return_value=service)
    return service
