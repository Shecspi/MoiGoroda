# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from premium.models import PremiumPlan, PremiumSubscription
from premium.services.subscriptions_management import (
    SubscriptionManagementService,
    format_days_text,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    ('days', 'expected'),
    [
        (1, '1 день'),
        (4, '4 дня'),
        (5, '5 дней'),
        (11, '11 дней'),
        (21, '21 день'),
    ],
)
def test_format_days_text_uses_russian_plural_form(days: int, expected: str) -> None:
    assert format_days_text(days) == expected


@pytest.fixture
def another_user(django_user_model: type[User]) -> User:
    return django_user_model.objects.create_user(
        username='another',
        password='testpass123',
        email='another@example.com',
    )


@pytest.fixture
def expired_subscription(user: User, premium_plan: PremiumPlan) -> PremiumSubscription:
    now = timezone.now()
    return PremiumSubscription.objects.create(
        user=user,
        plan=premium_plan,
        billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
        status=PremiumSubscription.Status.EXPIRED,
        started_at=now - timedelta(days=40),
        expires_at=now - timedelta(days=10),
    )


@pytest.mark.unit
@pytest.mark.django_db
class TestSubscriptionManagementService:
    def test_get_page_data_returns_active_and_expired_subscriptions(
        self,
        active_subscription: PremiumSubscription,
        another_user: User,
        premium_plan: PremiumPlan,
    ) -> None:
        expired_subscription = PremiumSubscription.objects.create(
            user=another_user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.EXPIRED,
            started_at=timezone.now() - timedelta(days=40),
            expires_at=timezone.now() - timedelta(days=10),
        )

        data = SubscriptionManagementService().get_page_data()

        assert [row.subscription.pk for row in data.active_subscriptions] == [
            active_subscription.pk
        ]
        assert [row.subscription.pk for row in data.expired_subscriptions] == [
            expired_subscription.pk
        ]

    def test_get_page_data_calculates_days_since_expiration(
        self,
        expired_subscription: PremiumSubscription,
    ) -> None:
        data = SubscriptionManagementService().get_page_data()

        assert data.expired_subscriptions[0].days_since_expired == 10
        assert data.expired_subscriptions[0].days_since_expired_text == '10 дней'

    def test_get_page_data_calculates_days_until_expiration(
        self,
        active_subscription: PremiumSubscription,
    ) -> None:
        data = SubscriptionManagementService().get_page_data()

        assert data.active_subscriptions[0].days_until_expired == 30
        assert data.active_subscriptions[0].days_until_expired_text == '30 дней'

    def test_get_page_data_groups_previous_subscriptions_with_active_user(
        self,
        user: User,
        premium_plan: PremiumPlan,
        active_subscription: PremiumSubscription,
    ) -> None:
        previous = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.EXPIRED,
            started_at=timezone.now() - timedelta(days=80),
            expires_at=timezone.now() - timedelta(days=50),
        )

        data = SubscriptionManagementService().get_page_data()

        assert len(data.active_subscriptions) == 1
        assert data.active_subscriptions[0].subscription.pk == active_subscription.pk
        assert [sub.pk for sub in data.active_subscriptions[0].previous_subscriptions] == [
            previous.pk
        ]
        assert data.expired_subscriptions == []

    def test_get_page_data_groups_expired_subscriptions_by_user(
        self,
        user: User,
        premium_plan: PremiumPlan,
    ) -> None:
        older = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.EXPIRED,
            started_at=timezone.now() - timedelta(days=90),
            expires_at=timezone.now() - timedelta(days=60),
        )
        latest = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.EXPIRED,
            started_at=timezone.now() - timedelta(days=40),
            expires_at=timezone.now() - timedelta(days=10),
        )

        data = SubscriptionManagementService().get_page_data()

        assert data.active_subscriptions == []
        assert len(data.expired_subscriptions) == 1
        assert data.expired_subscriptions[0].subscription.pk == latest.pk
        assert [sub.pk for sub in data.expired_subscriptions[0].previous_subscriptions] == [
            older.pk
        ]
