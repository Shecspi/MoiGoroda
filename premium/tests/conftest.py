"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

import pytest
from django.contrib.auth.models import User

from premium.adapters.payment_provider import CreatePaymentResult
from premium.models import (
    PremiumPayment,
    PremiumPlan,
    PremiumPlanFeature,
    PremiumSubscription,
)


@pytest.fixture
def user(django_user_model: type[User]) -> User:
    """Создаёт тестового пользователя."""
    return django_user_model.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com',
    )


@pytest.fixture
def premium_plan() -> PremiumPlan:
    """Создаёт тестовый тариф премиум-подписки."""
    return PremiumPlan.objects.create(
        slug='basic',
        name='Базовый',
        description='Базовый тариф',
        price_month=Decimal('299.00'),
        price_year=Decimal('2990.00'),
        currency='RUB',
        is_active=True,
        sort_order=0,
    )


@pytest.fixture
def premium_plan_cheap() -> PremiumPlan:
    """Создаёт более дешёвый тариф."""
    return PremiumPlan.objects.create(
        slug='lite',
        name='Лайт',
        description='Лёгкий тариф',
        price_month=Decimal('99.00'),
        price_year=Decimal('990.00'),
        currency='RUB',
        is_active=True,
        sort_order=1,
    )


@pytest.fixture
def premium_plan_feature(premium_plan: PremiumPlan) -> PremiumPlanFeature:
    """Создаёт преимущество тарифа."""
    return PremiumPlanFeature.objects.create(
        plan=premium_plan,
        text='Без рекламы',
        sort_order=0,
    )


@pytest.fixture
def subscription(
    user: User,
    premium_plan: PremiumPlan,
) -> PremiumSubscription:
    """Создаёт подписку в статусе PENDING."""
    return PremiumSubscription.objects.create(
        user=user,
        plan=premium_plan,
        billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
        status=PremiumSubscription.Status.PENDING,
        provider_payment_id='yookassa_123',
    )


@pytest.fixture
def active_subscription(
    user: User,
    premium_plan: PremiumPlan,
) -> PremiumSubscription:
    """Создаёт активную подписку."""
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    return PremiumSubscription.objects.create(
        user=user,
        plan=premium_plan,
        billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
        status=PremiumSubscription.Status.ACTIVE,
        started_at=now,
        expires_at=now + timedelta(days=30),
        provider_payment_id='yookassa_active',
    )


@pytest.fixture
def premium_payment(
    user: User,
    subscription: PremiumSubscription,
    premium_plan: PremiumPlan,
) -> PremiumPayment:
    """Создаёт платёж."""
    return PremiumPayment.objects.create(
        user=user,
        subscription=subscription,
        plan=premium_plan,
        yookassa_payment_id='22d6d597-000f-5000-9000-145f6df21d6f',
        amount_value=Decimal('299.00'),
        currency='RUB',
        billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
        description='Тариф Базовый на месяц',
        confirmation_url='https://yookassa.ru/pay/xxx',
        status=PremiumPayment.Status.PENDING,
    )


@pytest.fixture
def mock_payment_provider() -> MagicMock:
    """Мок платёжного провайдера."""
    provider = MagicMock()
    provider.create_payment.return_value = CreatePaymentResult(
        payment_id='yookassa_test_123',
        status='pending',
        confirmation_url='https://yookassa.ru/confirm/test',
        raw_response={'id': 'yookassa_test_123', 'status': 'pending'},
    )
    return provider


def make_webhook_payload(
    payment_id: str = '22d6d597-000f-5000-9000-145f6df21d6f',
    status: str = 'succeeded',
    event: str = 'payment.succeeded',
) -> dict[str, Any]:
    """Формирует минимальный валидный payload вебхука YooKassa."""
    return {
        'type': 'notification',
        'event': event,
        'object': {
            'id': payment_id,
            'status': status,
        },
    }
